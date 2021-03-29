
import astropy.units as u
from astropy.coordinates.earth import EarthLocation

from radiospectra.spectrogram2.spectrogram import BaseSpectrogram

__all__ = ['SWAVESSpectrogram', 'RFSSpectrogram', 'CALISTOSpectrogram', 'EOVSASpectrogram']


class SWAVESSpectrogram(BaseSpectrogram):
    """
    STEREO Waves or S/WAVES, SWAVES Spectrogram
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
    Parker Solar Probe FIELDS/Radio Frequency Spectrometer (RFS) Spectrogram
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
    """
    CALISTO Spectrogram from the e-CALISTO network
    """
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
    """
    Extend Owen Valley Array (EOVSA) Spectrogram
    """
    def __init__(self, *, meta, data, **kwargs):
        super().__init__(meta=meta, data=data, **kwargs)

    @property
    def polarisation(self):
        return self.meta['fits_meta']['POLARIZA']

    @classmethod
    def is_datasource_for(cls, *, meta, data, **kwargs):
        return meta['instrument'] == 'EOVSA' or meta['detector'] == 'EOVSA'

    # TODO fix time gaps for plots need to render them as gaps
    # can prob do when generateing proper pcolormesh gird but then prob doesn't belong here


class RSTNSpectrogram(BaseSpectrogram):

    @classmethod
    def is_datasource_for(cls, *, meta, data, **kwargs):
        return meta['instrument'] == 'RSTN'
