import ndcube

from radiospectra.utils import build_spectrogram_wcs
from radiospectra.spectrogram.meta import SpectrogramMeta

__all__ = ["GenericSpectrogram"]


class GenericSpectrogram(ndcube.NDCube):

    @classmethod
    def from_arrays(self, time, frequency, data, meta):
        gwcs = build_spectrogram_wcs(frequency, time)
        return super().__init__(data, gwcs, meta=meta)

    @property
    def time(self):
        return self.axis_world_coords('time')[0]

    @property
    def frequency(self):
        return self.axis_world_coords('frequency')[0]

