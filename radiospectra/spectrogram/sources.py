import numpy as np

import astropy.units as u
from astropy.coordinates.earth import EarthLocation

from radiospectra.spectrogram.spectrogram import BaseSpectrogram

__all__ = ['SWAVESSpectrogram', 'RFSSpectrogram', 'CALISTOSpectrogram', 'EOVSASpectrogram']


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
