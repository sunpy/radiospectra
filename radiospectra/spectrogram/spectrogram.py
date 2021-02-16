from pathlib import Path
from datetime import datetime

import cdflib
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.image import NonUniformImage

import astropy.units as u
from astropy.coordinates.earth import EarthLocation
from astropy.time import Time
from sunpy.io import fits
from sunpy.net import attrs as a
from sunpy.time import parse_time
from sunpy.util.datatype_factory_base import BasicRegistrationFactory


class SpectrogramFactory(BasicRegistrationFactory):
    def __call__(self, *args, **kwargs):
        if len(args) == 1 and not kwargs:
            arg = args[0]
            if isinstance(arg, (str, Path)):
                file = Path(arg)
                meta, data = self._read_file(file)

        return self._check_registered_widget(meta=meta, data=data, **kwargs)

    def _read_file(self, file):
        extension = file.suffix
        if extension == '.dat':
            meta, data = self._read_dat(file)
            return meta, data
        elif extension == '.cdf':
            meta, data = self._read_cdf(file)
            return meta, data
        elif extension in ('.fits', '.fit', '.fts'):
            meta, data = self._read_fits(file)
            return meta, data
        else:
            raise ValueError('Extension %s not supported.', extension)

    @staticmethod
    def _read_dat(file):
        if 'swaves' in file.name:
            name, prod, date, spacecraft, receiver = file.stem.split('_')
            # frequency range
            freqs = np.genfromtxt(file, max_rows=1) * u.kHz
            # bg which is already subtracted from data
            bg = np.genfromtxt(file, skip_header=1, max_rows=1)
            # data
            data = np.genfromtxt(file, skip_header=2)
            times = data[:, 0] * u.min
            data = data[:, 1:].T + bg.reshape(-1, 1)

            meta = {
                'instrument': name,
                'observatory': f'STEREO {spacecraft.upper()}',
                'product': prod,
                'start_time': Time(datetime.strptime('20201128', '%Y%m%d')),
                'wavelength': a.Wavelength(freqs[0], freqs[-1]),
                'detector': receiver
            }
            meta['freqs'] = freqs
            meta['times'] = times
            meta['end_time'] = meta['start_time'] + times[-1]
            return meta, data

    @staticmethod
    def _read_cdf(file):
        cdf = cdflib.CDF(file)
        cdf_meta = cdf.globalattsget()
        if (cdf_meta.get('Project', '') == 'PSP'
            and cdf_meta.get('Source_name') == 'PSP_FLD>Parker Solar Probe FIELDS'
            and 'Radio Frequency Spectrometer' in cdf_meta.get('Descriptor')):
            short, _long = cdf_meta['Descriptor'].split('>')
            detector = short[4:].lower()

            times, data, freqs = [cdf.varget(name) for name in
                                  [f'epoch_{detector}_auto_averages_ch0_V1V2',
                                   f'psp_fld_l2_rfs_{detector}_auto_averages_ch0_V1V2',
                                   f'frequency_{detector}_auto_averages_ch0_V1V2']]

            times = Time(times<<u.ns, format='cdf_tt2000')
            freqs = freqs[0,:] << u.Hz
            data = data.T << u.Unit('Volt**2/Hz')

            meta = {
                'cdf_meta' : cdf_meta,
                'detector' : detector,
                'instrument': 'FIELDS/RFS',
                'observatory': 'PSP',
                'start_time': times[0],
                'end_time': times[-1],
                'wavelength': a.Wavelength(freqs.min(), freqs.max()),
                'times': times,
                'freqs': freqs
            }
            return meta, data

    @staticmethod
    def _read_fits(file):
        hd_pairs = fits.read(file)

        if 'e-CALLISTO' in hd_pairs[0].header.get('CONTENT', ''):
            data = hd_pairs[0].data
            times = hd_pairs[1].data['TIME'].flatten() * u.s
            freqs = hd_pairs[1].data['FREQUENCY'].flatten() * u.MHz
            start_time = parse_time(hd_pairs[0].header['DATE-OBS']
                                    + ' ' + hd_pairs[0].header['TIME-OBS'])
            end_time = parse_time(hd_pairs[0].header['DATE-END']
                                  + ' ' + hd_pairs[0].header['TIME-END'])

            meta = {
                'fits_meta': hd_pairs[0].header,
                'detector': 'e-CALLISTO',
                'instrument': 'e-CALLISTO',
                'observatory': hd_pairs[0].header['INSTRUME'],
                'start_time': start_time,
                'end_time': end_time,
                'wavelength': a.Wavelength(freqs.min(), freqs.max()),
                'times': times,
                'freqs': freqs
            }
            return meta, data
        elif hd_pairs[0].header.get('TELESCOP', '') == 'EOVSA':
            times = Time(hd_pairs[2].data['mjd'] + hd_pairs[2].data['time'] / 1000.0 / 86400.,
                        format='mjd')
            freqs = hd_pairs[1].data['sfreq'] * u.GHz
            data = hd_pairs[0].data
            start_time = parse_time(hd_pairs[0].header['DATE_OBS'])
            end_time = parse_time(hd_pairs[0].header['DATE_END'])

            meta = {
                'fits_meta': hd_pairs[0].header,
                'detector': 'EOVSA',
                'instrument': 'EOVSA',
                'observatory': 'Owens Valley',
                'start_time': start_time,
                'end_time': end_time,
                'wavelength': a.Wavelength(freqs.min(), freqs.max()),
                'times': times,
                'freqs': freqs
            }
            return meta, data


class PcolormeshPlotMixin:
    """
    Class provides plotting functions using `~pcolormesh`
    """
    def plotc(self, axes=None, **kwargs):
        """
        Plot the spectrogram

        Parameters
        ----------
        axes : `matplotlib.axis.Axes` Optional
            The axes where the plot will be added

        kwargs :
            Arguments pass to the plot call `pcolormesh`
        Returns
        -------

        """
        if axes is None:
            fig, axes = plt.subplots()

        if hasattr(self.data, 'value'):
            data = self.data.value
        else:
            data = self.data
        axes.pcolormesh(self.times.datetime, self.frequencies.value, data,
                        shading='auto', **kwargs)


class NonUniformImagePlotMixin:
    """
    Class provides plotting functions using `NonUniformImage`
    """
    def plotim(self, fig=None, axes=None):
        if axes is None:
            fig, axes = plt.subplots()

        im = NonUniformImage(axes, interpolation=None)
        im.set_data(self.times.value, self.freqs.value, self.data)
        axes.images.append(im)


class BaseSpectrogram(PcolormeshPlotMixin, NonUniformImagePlotMixin):
    """
    Base Spectrogram class all spectrogram inherit from this class.

    Attributes
    ----------
    meta : `dict-like`
        Meta data about the
    data : `numpy.ndarra`
        The spectrogram data
    """
    _registry = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if hasattr(cls, 'is_datasource_for'):
            cls._registry[cls] = cls.is_datasource_for

    def __init__(self, meta, data, *args, **kwargs):
        """

        Parameters
        ----------
        meta
        data
        args
        kwargs
        """
        self.meta = meta
        self.data = data

    @property
    def observatory(self):
        """
        The name of the instrument which recorded the spectrogram.
        """
        return self.meta['observatory'].upper()

    @property
    def instrument(self):
        """
        The name of the instrument which recorded the spectrogram.
        """
        return self.meta['instrument'].upper()

    @property
    def detector(self):
        """
        The detector which recorded the spectrogram
        """
        return self.meta['detector'].upper()

    @property
    def start_time(self):
        """
        The start time of the spectrogram
        """
        return self.meta['start_time']

    @property
    def end_time(self):
        """
        The end time of the spectrogram
        """
        return self.meta['end_time']

    @property
    def wavelength(self):
        """
        The wavelength range of the spectrogram
        """
        return self.meta['wavelength']

    @property
    def times(self):
        """
        The times of the spectrogram data
        """
        return self.meta['times']

    @property
    def frequencies(self):
        """
        The frequencies of the spectrogram data
        """
        return self.meta['freqs']

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.observatory}, {self.instrument}, {self.detector}'\
               f' {self.wavelength}, {self.start_time}-{self.end_time}>'


class SWAVESSpectrogram(BaseSpectrogram):
    """
    STEREO Waves or S/WAVES, SWAVES spectrogram
    """
    def __init__(self, *, meta, data, **kwargs):
        super().__init__(meta=meta, data=data, **kwargs)

    @property
    def receiver(self):
        """
        The name of the receiver
        """
        return self.meta['receiver']

    @classmethod
    def is_datasource_for(cls, *, meta, data, **kwargs):
        return meta['instrument'] == 'swaves'


class RFSSpectrogram(BaseSpectrogram):
    """
    Parker Solar Probe FIELDS/ Radio Frequency Spectrometer (RFS) spectrogram
    """
    def __init__(self, *, meta, data, **kwargs):
        super().__init__(meta=meta, data=data, **kwargs)


    @property
    def level(self):
        return self.meta['cdf_meta']['Data_type'].split('>')[0]

    @property
    def version(self):
        return int(self.meta['cdf_meta']['Data_version'])

    @classmethod
    def is_datasource_for(cls, *, meta, data, **kwargs):
        return (meta['observatory'] == 'PSP' and meta['instrument'] == 'FIELDS/RFS'
                and meta['detector'] in ('lfr', 'hfr'))


class CALISTOSpectrogram(BaseSpectrogram):
    def __init__(self, *, meta, data, **kwargs):
        super().__init__(meta=meta, data=data, **kwargs)

    @property
    def observatory_location(self):
        lat = self.meta['fits_meta']['OBS_LAT'] * u.deg * 1.0 if \
            self.meta['fits_meta']['OBS_LAC'] == 'N' else -1.0
        lon = self.meta['fits_meta']['OBS_LON'] * u.deg * 1.0 if \
            self.meta['fits_meta']['OBS_LOC'] == 'E' else -1.0
        height = self.meta['fits_meta']['OBS_ALT'] * u.m
        return EarthLocation(lat=lat, lon=lon, height=height)

    @classmethod
    def is_datasource_for(cls, *, meta, data, **kwargs):
        return meta['instrument'] == 'e-CALLISTO' or meta['detector'] == 'e-CALLISTO'


class EOVSASpectrogram(BaseSpectrogram):
    def __init__(self, *, meta, data, **kwargs):
        super().__init__(meta=meta, data=data, **kwargs)

    @property
    def polarisation(self):
        return self.meta['fits_meta']['POLARIZA']

    @classmethod
    def is_datasource_for(cls, *, meta, data, **kwargs):
        return meta['instrument'] == 'EOVSA' or meta['detector'] == 'EOVSA'

    # TODO ask EOVSA team what to do here. Currently just dropping times which are not monotonically
    #  increasing.
    def fix_times(self):
        dt = np.diff((self.times-self.times[0]).to('s'))
        good_indices = np.hstack([[True], dt > 0])
        self.meta['times'] = self.times[good_indices]
        self.data = self.data[:, good_indices]


Spectrogram = SpectrogramFactory(registry=BaseSpectrogram._registry)
