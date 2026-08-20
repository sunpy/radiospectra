import astropy.units as u
from astropy.time import Time

from sunpy.net import attrs as a

from radiospectra.spectrogram.meta import SpectrogramMeta
from radiospectra.spectrogram.spectrogrambase import GenericSpectrogram

__all__ = ["RFSSpectrogram", "RFSMeta"]


class RFSMeta(SpectrogramMeta):
    """Metadata for PSP FIELDS/RFS spectrograms."""

    @property
    def processing_level(self) -> str | None:
        """The data processing level."""
        cdf_globals = self.get("cdf_globals")
        if cdf_globals:
            data_type = cdf_globals.get("Data_type")
            if data_type is None:
                return None
            if isinstance(data_type, list) or hasattr(data_type, "tolist"):
                data_type = data_type[0]
            return data_type.split(">")[0]
        return None

    @property
    def version(self) -> int | None:
        """The data version."""
        cdf_globals = self.get("cdf_globals")
        if cdf_globals:
            data_version = cdf_globals.get("Data_version")
            if data_version is None:
                return None
            if isinstance(data_version, list) or hasattr(data_version, "tolist"):
                data_version = data_version[0]
            return int(data_version)
        return None


class RFSSpectrogram(GenericSpectrogram):
    """
    Parker Solar Probe FIELDS/Radio Frequency Spectrometer (RFS) Spectrogram.

    >>> import radiospectra.net
    >>> from sunpy.net import Fido, attrs as a
    >>> from radiospectra.spectrogram import Spectrogram
    >>> from radiospectra.net import attrs as ra
    >>> query = Fido.search(a.Time('2019/10/05 23:00', '2019/10/06 00:59'),  #doctest: +REMOTE_DATA
    ...                     a.Instrument.rfs)  #doctest: +REMOTE_DATA
    >>> downloaded = Fido.fetch(query[0][0])  #doctest: +REMOTE_DATA
    >>> spec = Spectrogram(downloaded[0])  #doctest: +REMOTE_DATA
    >>> spec  #doctest: +REMOTE_DATA
    <RFSSpectrogram PSP, FIELDS/RFS, LFR 10.546879882812501 kHz - 1687.5 kHz, 2019-10-05T00:01:32.395 to 2019-10-05T22:16:30.493>
    >>> spec.plot()  #doctest: +REMOTE_DATA
    <matplotlib.collections.QuadMesh object at ...>
    """

    def __init__(self, data, meta, **kwargs):
        if not isinstance(meta, RFSMeta):
            meta = RFSMeta(meta)
        super().__init__(meta=meta, data=data, **kwargs)

    @property
    def processing_level(self):
        return self.meta.processing_level

    @property
    def version(self):
        return self.meta.version

    @classmethod
    def is_datasource_for(cls, data_or_header, meta_or_raw, **kwargs):
        meta = data_or_header if hasattr(data_or_header, "get") else meta_or_raw
        if not hasattr(meta, "get"):
            return False

        if (
            meta.get("observatory") == "PSP"
            and meta.get("instrument") == "FIELDS/RFS"
            and meta.get("detector") in ("lfr", "hfr")
        ):
            return True

        cdf_globals = meta.get("cdf_globals")
        if not cdf_globals:
            return False
        return (
            cdf_globals.get("Project", "")[0] == "PSP"
            and cdf_globals.get("Source_name", [""])[0] == "PSP_FLD>Parker Solar Probe FIELDS"
            and "Radio Frequency Spectrometer" in cdf_globals.get("Descriptor", [""])[0]
        )

    @classmethod
    def from_raw(cls, header, raw_object):
        cdf = raw_object
        cdf_globals = header["cdf_globals"]
        short, _long = cdf_globals["Descriptor"][0].split(">")
        detector = short[4:].lower()
        times, data, freqs = (
            cdf.varget(name)
            for name in [
                f"epoch_{detector}_auto_averages_ch0_V1V2",
                f"psp_fld_l2_rfs_{detector}_auto_averages_ch0_V1V2",
                f"frequency_{detector}_auto_averages_ch0_V1V2",
            ]
        )
        times = Time("J2000.0", scale="tt") + (times << u.ns)
        freqs = freqs[0, :] << u.Hz
        data = data.T << u.Unit("Volt**2/Hz")
        meta = RFSMeta(
            {
                "cdf_globals": cdf_globals,
                "detector": detector,
                "instrument": "FIELDS/RFS",
                "observatory": "PSP",
                "start_time": times[0],
                "end_time": times[-1],
                "wavelength": a.Wavelength(freqs.min(), freqs.max()),
                "times": times,
                "freqs": freqs,
            }
        )
        return cls(data, meta)
