from pathlib import Path

from radiospectra import data
from radiospectra.spectrogram import Spectrogram


def test_eovsa():
    file = Path(data.__file__).parent / 'EOVSA_XPall_20210213.fts'
    Spectrogram(file)
