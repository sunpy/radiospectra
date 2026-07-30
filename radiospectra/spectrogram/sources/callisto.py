import astropy.units as u
from astropy.coordinates import EarthLocation, SkyCoord

from radiospectra.spectrogram.meta import SpectrogramMeta
from radiospectra.spectrogram.spectrogrambase import GenericSpectrogram

__all__ = ["CALISTOSpectrogram", "CALISTOMeta"]


class CALISTOMeta(SpectrogramMeta):
    """Metadata for e-CALLISTO spectrograms."""

    @property
    def observer_coordinate(self) -> SkyCoord | None:
        """The coordinate of the observatory."""
        fits_meta = self.get("fits_meta")
        if fits_meta:
            lat_val = fits_meta.get("OBS_LAT")
            lon_val = fits_meta.get("OBS_LON")
            if lat_val is None or lon_val is None:
                return None
            lat = lat_val * u.deg * (1.0 if fits_meta.get("OBS_LAC") == "N" else -1.0)
            lon = lon_val * u.deg * (1.0 if fits_meta.get("OBS_LOC") == "E" else -1.0)
            height = fits_meta.get("OBS_ALT", 0) * u.m
            loc = EarthLocation(lat=lat, lon=lon, height=height)
            obstime = self.get("start_time")
            if obstime is not None:
                return SkyCoord(loc.get_gcrs(obstime))
            return SkyCoord(loc.get_itrs())
        return None


class CALISTOSpectrogram(GenericSpectrogram):
    """
    CALISTO Spectrogram from the e-CALISTO network.

    Examples
    --------
    >>> import radiospectra.net
    >>> from sunpy.net import Fido, attrs as a
    >>> from radiospectra.spectrogram import Spectrogram
    >>> from radiospectra.net import attrs as ra
    >>> query = Fido.search(a.Time('2019/10/05 23:00', '2019/10/06 00:59'),  #doctest: +REMOTE_DATA
    ...                     a.Instrument('eCALLISTO'), ra.Observatory('ALASKA'))  #doctest: +REMOTE_DATA
    >>> downloaded = Fido.fetch(query[0][0])  #doctest: +REMOTE_DATA
    >>> spec = Spectrogram(downloaded[0])  #doctest: +REMOTE_DATA
    >>> spec  #doctest: +REMOTE_DATA
    <CALISTOSpectrogram ALASKA, E-CALLISTO, E-CALLISTO 215000.0 kHz - 418937.98828125 kHz, 2019-10-05T23:00:00.757 to 2019-10-05T23:15:00.000>
    >>> spec.plot()  #doctest: +REMOTE_DATA
    <matplotlib.collections.QuadMesh object at ...>
    """

    def __init__(self, data, meta, **kwargs):
        if not isinstance(meta, CALISTOMeta):
            meta = CALISTOMeta(meta)
        super().__init__(meta=meta, data=data, **kwargs)

    @property
    def observatory_location(self):
        return self.meta.observer_coordinate

    @classmethod
    def is_datasource_for(cls, header, raw_object, **kwargs):
        # The factory passes the FITS header as the first argument
        return "e-CALLISTO" in header.get("CONTENT", "")

    @classmethod
    def from_raw(cls, header, raw_object):
        from sunpy.net import attrs as a
        from sunpy.time import parse_time

        hd_pairs = raw_object
        data = hd_pairs[0].data
        times = hd_pairs[1].data["TIME"].flatten() * u.s
        freqs = hd_pairs[1].data["FREQUENCY"].flatten() * u.MHz
        start_time = parse_time(hd_pairs[0].header["DATE-OBS"] + " " + hd_pairs[0].header["TIME-OBS"])
        try:
            end_time = parse_time(hd_pairs[0].header["DATE-END"] + " " + hd_pairs[0].header["TIME-END"])
        except ValueError:
            # See https://github.com/sunpy/radiospectra/issues/74
            time_comps = hd_pairs[0].header["TIME-END"].split(":")
            time_comps[0] = "00"
            fixed_time = ":".join(time_comps)
            date_offset = parse_time(hd_pairs[0].header["DATE-END"] + " " + fixed_time)
            end_time = date_offset + 1 * u.day

        times = start_time + times
        meta = {
            "fits_meta": hd_pairs[0].header,
            "detector": "e-CALLISTO",
            "instrument": "e-CALLISTO",
            "observatory": hd_pairs[0].header["INSTRUME"],
            "start_time": start_time,
            "end_time": end_time,
            "wavelength": a.Wavelength(freqs.min(), freqs.max()),
            "times": times,
            "freqs": freqs,
        }
        return cls(data, meta)
