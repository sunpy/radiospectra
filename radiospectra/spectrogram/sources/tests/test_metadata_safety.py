import pytest

from radiospectra.spectrogram.sources.rpw import RPWSpectrogram
from radiospectra.spectrogram.sources.eovsa import EOVSASpectrogram
from radiospectra.spectrogram.sources.rstn import RSTNSpectrogram


@pytest.mark.parametrize(
    "cls",
    [
        RPWSpectrogram,
        EOVSASpectrogram,
        RSTNSpectrogram,
    ],
)
def test_is_datasource_handles_missing_metadata(cls):
    meta = {}  # missing keys

    # Should not raise error
    result = cls.is_datasource_for(None, meta)

    assert result is False
