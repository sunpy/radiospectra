import struct
from pathlib import Path
from datetime import datetime

import cdflib
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.image import NonUniformImage

import astropy.units as u
from astropy.time import Time
from astropy.visualization import quantity_support
from sunpy.io import fits
from sunpy.net import attrs as a
from sunpy.time import parse_time
from sunpy.util.datatype_factory_base import BasicRegistrationFactory

quantity_support()

__all__ = ['SpectrogramFactory', 'Spectrogram', 'BaseSpectrogram']


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
        elif extension == '.srs':
            meta, data = self._read_srs(file)
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

            meta = {'instrument': name, 'observatory': f'STEREO {spacecraft.upper()}',
                    'product': prod, 'start_time': Time(datetime.strptime('20201128', '%Y%m%d')),
                    'wavelength': a.Wavelength(freqs[0], freqs[-1]), 'detector': receiver,
                    'freqs': freqs}

            meta['times'] = meta['start_time'] + times
            meta['end_time'] = meta['start_time'] + times[-1]
            return meta, data

    @staticmethod
    def _read_srs(file):
        with file.open('rb') as file:
            data = file.read()
            # Data is store as a series of records made of different numbers of bytes
            # General header information
            # 1		Year (last 2 digits)				Byte integer (unsigned)
            # 2		Month number (1 to 12)			    "
            # 3		Day (1 to 31)					    "
            # 4		Hour (0 to 23 UT)				    "
            # 5		Minute (0 to 59)				    "
            # 6		Second at start of scan (0 to 59)	"
            # 7		Site Number (0 to 255)			    "
            # 8		Number of bands in the record (2)	"
            #
            # Band 1 (A-band) header information
            # 9,10		Start Frequency (MHz)			    Word integer (16 bits)
            # 11,12		End Frequency (MHz)			        "
            # 13,14		Number of bytes in data record (401)"
            # 15		Analyser reference level		    Byte integer
            # 16		Analyser attenuation (dB)		    "
            #
            # Band 2 (B-band) header information
            # 17-24		As for band 1
            #
            # Spectrum Analyser data
            # 25-425	401 data bytes for band 1 (A-band)
            # 426-826	401 data bytes for band 2 (B-band)
            record_struc = struct.Struct('B'*8 + 'H'*3 + 'B'*2
                                         + 'H'*3 + 'B'*2 + 'B' * 401 + 'B' * 401)
            records = record_struc.iter_unpack(data)

            # Map of numeric records to locations
            site_map = {1: 'Palehua', 2: 'Holloman', 3: 'Learmonth', 4: 'San Vito'}

            df = pd.DataFrame([(*r[:18], np.array(r[18:419]), np.array(r[419:820]))
                              for r in records])
            df.columns = ['year', 'month', 'day', 'hour', 'minute', 'second', 'site', ' num_bands',
                          'start_freq1', 'end_freq1', 'num_bytes1', 'analyser_ref1',
                          'analyser_atten1', 'start_freq2', 'end_freq2', 'num_bytes2',
                          'analyser_ref2', 'analyser_atten2', 'spec1', 'spec2']

            # Hack to make to_datetime work - earliest dates seem to be 2000 and won't be
            # around in 3000!
            df['year'] = df['year'] + 2000
            df['time'] = pd.to_datetime(df[['year', 'month', 'day', 'hour', 'minute', 'second']])

            # Equations taken from document
            n = np.arange(1, 402)
            freq_a = (25 + 50 * (n - 1) / 400) * u.MHz
            freq_b = (75 + 105 * (n - 1) / 400) * u.MHz
            freqs = np.hstack([freq_a, freq_b])

            data = np.hstack([np.vstack(df[name].to_numpy()) for name in ['spec1', 'spec2']]).T
            times = Time(df['time'])

            meta = {'instrument': 'RSTN', 'observatory': site_map[df['site'][0]],
                    'start_time': times[0], 'end_time': times[-1], 'detector': 'RSTN',
                    'wavelength': a.Wavelength(freqs[0], freqs[-1]), 'freqs': freqs, 'times': times}

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

            times = Time(times << u.ns, format='cdf_tt2000')
            freqs = freqs[0, :] << u.Hz
            data = data.T << u.Unit('Volt**2/Hz')

            meta = {
                'cdf_meta': cdf_meta,
                'detector': detector,
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
            times = start_time + times
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
    def plot(self, axes=None, **kwargs):
        """
        Plot the spectrogram2

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
        else:
            fig = axes.get_figure()

        if hasattr(self.data, 'value'):
            data = self.data.value
        else:
            data = self.data

        title = f'{self.observatory}, {self.instrument}'
        if self.instrument != self.detector:
            title = f'{title}, {self.detector}'

        axes.set_title(title)
        axes.plot(self.times.datetime[[0, -1]], self.frequencies[[0, -1]],
                  linestyle='None', marker='None')
        axes.pcolormesh(self.times.datetime, self.frequencies.value, data[:-1, :-1],
                        shading='auto', **kwargs)
        axes.set_xlim(self.times.datetime[0], self.times.datetime[-1])
        locator = mdates.AutoDateLocator(minticks=4, maxticks=8)
        formatter = mdates.ConciseDateFormatter(locator)
        axes.xaxis.set_major_locator(locator)
        axes.xaxis.set_major_formatter(formatter)
        fig.autofmt_xdate()


class NonUniformImagePlotMixin:
    """
    Class provides plotting functions using `NonUniformImage`
    """
    def plotim(self, fig=None, axes=None, **kwargs):
        if axes is None:
            fig, axes = plt.subplots()

        im = NonUniformImage(axes, interpolation=None, **kwargs)
        im.set_data(mdates.date2num(self.times.datetime), self.frequencies.value, self.data)
        axes.images.append(im)


class BaseSpectrogram(PcolormeshPlotMixin, NonUniformImagePlotMixin):
    """
    Base Spectrogram class all spectrogram2 inherit from this class.

    Attributes
    ----------
    meta : `dict-like`
        Meta data for the specogram
    data : `numpy.ndarray`
        The spectrogram data itself a 2D array

    """
    _registry = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if hasattr(cls, 'is_datasource_for'):
            cls._registry[cls] = cls.is_datasource_for

    def __init__(self, meta, data, *args, **kwargs):
        self.meta = meta
        self.data = data

    @property
    def observatory(self):
        """
        The name of the observatory which recorded the spectrogram.
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
        The detector which recorded the spectrogram.
        """
        return self.meta['detector'].upper()

    @property
    def start_time(self):
        """
        The start time of the spectrogram.
        """
        return self.meta['start_time']

    @property
    def end_time(self):
        """
        The end time of the spectrogram.
        """
        return self.meta['end_time']

    @property
    def wavelength(self):
        """
        The wavelength range of the spectrogram.
        """
        return self.meta['wavelength']

    @property
    def times(self):
        """
        The times of the spectrogram.
        """
        return self.meta['times']

    @property
    def frequencies(self):
        """
        The frequencies of the spectrogram.
        """
        return self.meta['freqs']

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.observatory}, {self.instrument}, {self.detector}'\
               f' {self.wavelength}, {self.start_time}-{self.end_time}>'


Spectrogram = SpectrogramFactory(registry=BaseSpectrogram._registry)
