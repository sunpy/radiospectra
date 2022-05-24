import astropy.units as u
from sunpy.net import attrs as a
from sunpy.net.dataretriever.client import GenericClient, QueryResponse
from sunpy.net.scraper import Scraper
from sunpy.time import TimeRange

__all__ = ["WAVESClient"]


RECEIVER_FREQUENCIES = {
    "rad1": a.Wavelength(20 * u.kHz, 1040 * u.kHz),
    "rad2": a.Wavelength(1.075 * u.MHz, 13.825 * u.MHz),
}

RECEIVER_EXT = {
    "rad1": "R1",
    "rad2": "R2",
}


class WAVESClient(GenericClient):
    """
    Provides access to `WIND WAVES <https://solar- radio.gsfc.nasa.gov/wind/instrument.html>`__ radio
    `data archive <https://solar-radio.gsfc.nasa.gov/data/wind>`__.

    Examples
    --------
    >>> import radiospectra.net
    >>> from sunpy.net import Fido, attrs as a
    >>> results = Fido.search(a.Time("2010/10/01", "2010/10/02"),
    ...                       a.Instrument('WAVES'))  # doctest: +REMOTE_DATA
    >>> results #doctest: +REMOTE_DATA
    <sunpy.net.fido_factory.UnifiedResponse object at ...>
    Results from 1 Provider:
    <BLANKLINE>
    4 Results from the WAVESClient:
    <BLANKLINE>
           Start Time               End Time        ... Provider     Wavelength
                                                    ...                 kHz
    ----------------------- ----------------------- ... -------- -----------------
    2010-10-01 00:00:00.000 2010-10-01 23:59:59.999 ...     NASA    20.0 .. 1040.0
    2010-10-02 00:00:00.000 2010-10-02 23:59:59.999 ...     NASA    20.0 .. 1040.0
    2010-10-01 00:00:00.000 2010-10-01 23:59:59.999 ...     NASA 1075.0 .. 13825.0
    2010-10-02 00:00:00.000 2010-10-02 23:59:59.999 ...     NASA 1075.0 .. 13825.0
    <BLANKLINE>
    <BLANKLINE>
    """

    baseurl = r"https://solar-radio.gsfc.nasa.gov/data/wind/{Wavelength}/{year}/{Wavelength}/" r"(\d){{8}}.{ext}"

    pattern = r"{}/{Wavelength}/{year:4d}/{Wavelength}/{year:4d}{month:2d}{day:2d}.{ext}"

    @classmethod
    def _check_wavelengths(cls, wavelength):
        """
        Check for overlap between given wavelength and receiver frequency coverage defined in.

        `RECEIVER_FREQUENCIES`.

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
            # Overlaps but not contained in, either max in lfr or min hfr
            if wavelength.min in RECEIVER_FREQUENCIES["rad2"] or wavelength.max in RECEIVER_FREQUENCIES["rad2"]:
                receivers.append("rad2")
            if wavelength.min in RECEIVER_FREQUENCIES["rad1"] or wavelength.max in RECEIVER_FREQUENCIES["rad1"]:
                receivers.append("rad1")
            # min in lfr and max in hfr
            # min and max of combined lft and hfr contained in give wavelength range
            if a.Wavelength(RECEIVER_FREQUENCIES["rad1"].min, RECEIVER_FREQUENCIES["rad2"].max) in wavelength:
                receivers = ["rad1", "rad2"]
            # If we get here the is no overlap so set to empty list
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
                urlpattern = self.baseurl.format(Wavelength=receiver, year=year, ext=RECEIVER_EXT[receiver])
                scraper = Scraper(urlpattern, regex=True)
                filesmeta = scraper._extract_files_meta(tr, extractor=self.pattern)
                for i in filesmeta:
                    rowdict = self.post_search_hook(i, matchdict)
                    metalist.append(rowdict)

        return QueryResponse(metalist, client=self)

    def post_search_hook(self, exdict, matchdict):
        """
        This method converts 'rad1' and 'rad1' in the url's metadata to the frequency ranges of for.

        low and high frequency receivers and removes the ext.
        """
        rowdict = super().post_search_hook(exdict, matchdict)
        rowdict.pop("ext", None)
        if rowdict["Wavelength"] == "rad1":
            fr = RECEIVER_FREQUENCIES["rad1"]
            rowdict["Wavelength"] = u.Quantity([float(fr.min.value), float(fr.max.value)], unit=fr.unit)
        elif rowdict["Wavelength"] == "rad2":
            fr = RECEIVER_FREQUENCIES["rad2"]
            rowdict["Wavelength"] = u.Quantity([float(fr.min.value), float(fr.max.value)], unit=fr.unit)
        return rowdict

    @classmethod
    def register_values(cls):
        adict = {
            a.Instrument: [("WAVES", "WIND - Waves")],
            a.Source: [("WIND", "WIND")],
            a.Provider: [("NASA", "NASA Goddard Space Flight Center")],
            a.Wavelength: [("*")],
        }
        return adict
