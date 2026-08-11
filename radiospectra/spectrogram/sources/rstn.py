import gzip
import struct

import numpy as np
import pandas as pd

import astropy.units as u
from astropy.time import Time

from sunpy.net import attrs as a

from radiospectra.spectrogram.meta import SpectrogramMeta
from radiospectra.spectrogram.spectrogrambase import GenericSpectrogram

__all__ = ["RSTNSpectrogram", "RSTNMeta"]


class RSTNMeta(SpectrogramMeta):
    """Metadata for RSTN spectrograms."""

    pass


class RSTNSpectrogram(GenericSpectrogram):
    """
    Radio Solar Telescope Network.

    Examples
    --------
    >>> import radiospectra.net
    >>> from sunpy.net import Fido, attrs as a
    >>> from radiospectra.spectrogram import Spectrogram
    >>> query = Fido.search(a.Time('2017/09/07 00:00', '2017/09/07 23:00'), a.Instrument.rstn)  #doctest: +REMOTE_DATA
    >>> downloaded = Fido.fetch(query[0][0])  #doctest: +REMOTE_DATA
    >>> spec = Spectrogram(downloaded[0])  #doctest: +REMOTE_DATA
    >>> spec  #doctest: +REMOTE_DATA
    <RSTNSpectrogram LEARMONTH, RSTN, RSTN 25000.0 kHz - 180000.0 kHz, 2017-09-06T22:31:51.000 to 2017-09-07T10:06:36.000>
    >>> spec.plot()  #doctest: +REMOTE_DATA
    <matplotlib.collections.QuadMesh object at ...>
    """

    def __init__(self, data, meta, **kwargs):
        if not isinstance(meta, RSTNMeta):
            meta = RSTNMeta(meta)
        super().__init__(meta=meta, data=data, **kwargs)

    @classmethod
    def is_datasource_for(cls, data_or_header, meta_or_raw, **kwargs):
        meta = data_or_header if hasattr(data_or_header, "get") else meta_or_raw
        if not hasattr(meta, "get"):
            return False
        return meta.get("instrument") == "RSTN"

    @classmethod
    def from_raw(cls, header, raw_object):
        file = header["file_path"]
        with file.open("rb") as buff:
            data = buff.read()
            if file.suffixes[-1] == ".gz":
                data = gzip.decompress(data)
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
        record_struc = struct.Struct("B" * 8 + "H" * 3 + "B" * 2 + "H" * 3 + "B" * 2 + "B" * 401 + "B" * 401)
        records = record_struc.iter_unpack(data)
        # Map of numeric records to locations
        site_map = {1: "Palehua", 2: "Holloman", 3: "Learmonth", 4: "San Vito"}
        df = pd.DataFrame([(*r[:18], np.array(r[18:419]), np.array(r[419:820])) for r in records])
        df.columns = [
            "year",
            "month",
            "day",
            "hour",
            "minute",
            "second",
            "site",
            " num_bands",
            "start_freq1",
            "end_freq1",
            "num_bytes1",
            "analyser_ref1",
            "analyser_atten1",
            "start_freq2",
            "end_freq2",
            "num_bytes2",
            "analyser_ref2",
            "analyser_atten2",
            "spec1",
            "spec2",
        ]
        # Hack to make to_datetime work - earliest dates seem to be 2000 and won't be
        # around in 3000!
        df["year"] = df["year"] + 2000
        df["time"] = pd.to_datetime(df[["year", "month", "day", "hour", "minute", "second"]])
        # Equations taken from document
        n = np.arange(1, 402)
        freq_a = (25 + 50 * (n - 1) / 400) * u.MHz
        freq_b = (75 + 105 * (n - 1) / 400) * u.MHz
        freqs = np.hstack([freq_a, freq_b])
        data = np.hstack([np.vstack(df[name].to_numpy()) for name in ["spec1", "spec2"]]).T
        times = Time(
            Time(df["time"]), format="iso"
        )  # TODO update once datetime format is supported by current plotters
        meta = RSTNMeta(
            {
                "instrument": "RSTN",
                "observatory": site_map[df["site"][0]],
                "start_time": times[0],
                "end_time": times[-1],
                "detector": "RSTN",
                "wavelength": a.Wavelength(freqs[0], freqs[-1]),
                "freqs": freqs,
                "times": times,
            }
        )
        return cls(data, meta)
