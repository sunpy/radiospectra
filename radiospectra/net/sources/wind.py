import astropy.units as u

from sunpy.net import attrs as a
from sunpy.net.dataretriever.client import GenericClient, QueryResponse
from sunpy.net.scraper import Scraper
from sunpy.time.timerange import TimeRange

__all__ = ["WAVESClient"]

RECEIVER_FREQUENCIES = {
    "rad1": a.Wavelength(20 * u.kHz, 1040 * u.kHz),
    "rad2": a.Wavelength(1.075 * u.MHz, 13.825 * u.MHz),
}

RECEIVER_EXTENSIONS = {
    "rad1": "R1",
    "rad2": "R2",
}


class WAVESClient(GenericClient):
    """
    Provides access to WIND/WAVES IDL binary data hosted at
    `NASA Goddard Space Physics Data Facility (SPDF)
    <https://spdf.gsfc.nasa.gov/pub/data/wind/waves/>`__.

    Examples
    --------
    >>> import radiospectra.net
    >>> from sunpy.net import Fido, attrs as a
    >>> results = Fido.search(a.Time("2020/01/01", "2020/01/02"),
    ...                       a.Instrument("WAVES"))  # doctest: +REMOTE_DATA
    >>> results  # doctest: +REMOTE_DATA
    <sunpy.net.fido_factory.UnifiedResponse object at ...>
    Results from 1 Provider:
    <BLANKLINE>
    4 Results from the WAVESClient:
    <BLANKLINE>
           Start Time               End Time        Instrument Source Provider     Wavelength
                                                                                        kHz
    ----------------------- ----------------------- ---------- ------ -------- -----------------
    2020-01-01 00:00:00.000 2020-01-01 23:59:59.999      WAVES   WIND     SPDF    20.0 .. 1040.0
    2020-01-02 00:00:00.000 2020-01-02 23:59:59.999      WAVES   WIND     SPDF    20.0 .. 1040.0
    2020-01-01 00:00:00.000 2020-01-01 23:59:59.999      WAVES   WIND     SPDF 1075.0 .. 13825.0
    2020-01-02 00:00:00.000 2020-01-02 23:59:59.999      WAVES   WIND     SPDF 1075.0 .. 13825.0
    <BLANKLINE>
    <BLANKLINE>
    """

    pattern = (
        r"https://spdf.gsfc.nasa.gov/pub/data/wind/waves/{receiver}_idl_binary/{year_path}/"
        r"wind_waves_{receiver}_{{year:4d}}{{month:2d}}{{day:2d}}.{ext}"
    )

    @classmethod
    def _check_wavelengths(cls, wavelength):
        """
        Check for overlap between given wavelength and receiver frequency coverage
        defined in ``RECEIVER_FREQUENCIES``.

        Parameters
        ----------
        wavelength : `sunpy.net.attrs.Wavelength`
            Input wavelength range to check

        Returns
        -------
        `list`
            List of receivers names or empty list if no overlap
        """
        # Input wavelength range is completely contained in one receiver range
        receivers = [k for k, v in RECEIVER_FREQUENCIES.items() if wavelength in v]
        # If not defined need to continue
        if not receivers:
            # Overlaps but not contained in, either max in low-frequency or min in high-frequency receiver
            if wavelength.min in RECEIVER_FREQUENCIES["rad2"] or wavelength.max in RECEIVER_FREQUENCIES["rad2"]:
                receivers.append("rad2")
            if wavelength.min in RECEIVER_FREQUENCIES["rad1"] or wavelength.max in RECEIVER_FREQUENCIES["rad1"]:
                receivers.append("rad1")
            # min in rad1 and max in rad2
            # min and max of combined rad1 and rad2 contained in given wavelength range
            if a.Wavelength(RECEIVER_FREQUENCIES["rad1"].min, RECEIVER_FREQUENCIES["rad2"].max) in wavelength:
                receivers = ["rad1", "rad2"]
        return receivers

    def search(self, *args, **kwargs):
        """
        Query this client for a list of results.

        Parameters
        ----------
        *args: `tuple`
            `sunpy.net.attrs` objects representing the query.
        **kwargs: `dict`
            Any extra keywords to refine the search.

        Returns
        -------
        A `QueryResponse` instance containing the query result.
        """
        matchdict = self._get_match_dict(*args, **kwargs)
        req_wave = matchdict.get("Wavelength", None)
        receivers = RECEIVER_FREQUENCIES.keys()
        if req_wave is not None:
            receivers = self._check_wavelengths(req_wave)

        metalist = []
        start_year = matchdict["Start Time"].datetime.year
        end_year = matchdict["End Time"].datetime.year
        tr = TimeRange(matchdict["Start Time"], matchdict["End Time"])
        for receiver in receivers:
            for year in range(start_year, end_year + 1):
                pattern = (
                    self.pattern.replace("{receiver}", receiver)
                    .replace("{ext}", RECEIVER_EXTENSIONS[receiver])
                    .replace("{year_path}", str(year))
                )
                scraper = Scraper(format=pattern)
                filesmeta = scraper._extract_files_meta(tr)
                for i in filesmeta:
                    i["receiver"] = receiver
                    rowdict = self.post_search_hook(i, matchdict)
                    metalist.append(rowdict)

        return QueryResponse(metalist, client=self)

    def post_search_hook(self, exdict, matchdict):
        """
        Convert receiver metadata to the receiver frequency ranges.
        """
        rowdict = super().post_search_hook(exdict, matchdict)
        receiver = rowdict.pop("receiver")
        fr = RECEIVER_FREQUENCIES[receiver]
        rowdict["Wavelength"] = u.Quantity([float(fr.min.value), float(fr.max.value)], unit=fr.unit)
        return rowdict

    @classmethod
    def register_values(cls):
        adict = {
            a.Instrument: [("WAVES", "WIND - WAVES")],
            a.Source: [("WIND", "WIND")],
            a.Provider: [("SPDF", "NASA Goddard Space Physics Data Facility")],
            a.Wavelength: [("*")],
        }
        return adict
