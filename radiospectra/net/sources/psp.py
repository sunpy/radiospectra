import astropy.units as u
from sunpy.net import attrs as a
from sunpy.net.dataretriever.client import GenericClient, QueryResponse
from sunpy.net.scraper import Scraper
from sunpy.time.timerange import TimeRange

__all__ = ["RFSClient"]

RECEIVER_FREQUENCIES = {
    "rfs_lfr": a.Wavelength(10 * u.kHz, 1.7 * u.MHz),
    "rfs_hfr": a.Wavelength(1.3 * u.MHz, 19.2 * u.MHz),
}


class RFSClient(GenericClient):
    """
    Provides access to Parker Solar Probe FIELDS Radio Frequency Spectrometer data
    `archive <https://spdf.gsfc.nasa.gov/pub/data/psp/fields/>`__ at
    `NASA Goddard Space Physics Data Facility (SPDF) <https://spdf.gsfc.nasa.gov>`__.

    Examples
    --------
    >>> import radiospectra.net
    >>> from sunpy.net import Fido, attrs as a
    >>> results = Fido.search(a.Time("2019/10/02", "2019/10/05"),
    ...                        a.Instrument('rfs'))  #doctest: +REMOTE_DATA
    >>> results  #doctest: +REMOTE_DATA
    <sunpy.net.fido_factory.UnifiedResponse object at ...>
    Results from 1 Provider:
    <BLANKLINE>
    8 Results from the RFSClient:
    <BLANKLINE>
           Start Time               End Time        ... Provider     Wavelength
                                                    ...                 kHz
    ----------------------- ----------------------- ... -------- -----------------
    2019-10-02 00:00:00.000 2019-10-02 23:59:59.999 ...     SPDF    10.0 .. 1700.0
    2019-10-03 00:00:00.000 2019-10-03 23:59:59.999 ...     SPDF    10.0 .. 1700.0
    2019-10-04 00:00:00.000 2019-10-04 23:59:59.999 ...     SPDF    10.0 .. 1700.0
    2019-10-05 00:00:00.000 2019-10-05 23:59:59.999 ...     SPDF    10.0 .. 1700.0
    2019-10-02 00:00:00.000 2019-10-02 23:59:59.999 ...     SPDF 1300.0 .. 19200.0
    2019-10-03 00:00:00.000 2019-10-03 23:59:59.999 ...     SPDF 1300.0 .. 19200.0
    2019-10-04 00:00:00.000 2019-10-04 23:59:59.999 ...     SPDF 1300.0 .. 19200.0
    2019-10-05 00:00:00.000 2019-10-05 23:59:59.999 ...     SPDF 1300.0 .. 19200.0
    <BLANKLINE>
    <BLANKLINE>
    """

    baseurl = (
        r"https://spdf.gsfc.nasa.gov/pub/data/psp/fields/l2/{Wavelength}/"
        r"{year}/psp_fld_l2_(\w){{7}}_(\d){{8}}_v(\d){{2}}.cdf"
    )
    pattern = r"{}/{Wavelength}/{year:4d}/" r"psp_fld_l2_{Wavelength}_{year:4d}{month:2d}{day:2d}_v{:2d}.cdf"

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
            if wavelength.min in RECEIVER_FREQUENCIES["rfs_hfr"] or wavelength.max in RECEIVER_FREQUENCIES["rfs_hfr"]:
                receivers.append("rfs_hfr")
            if wavelength.min in RECEIVER_FREQUENCIES["rfs_lfr"] or wavelength.max in RECEIVER_FREQUENCIES["rfs_lfr"]:
                receivers.append("rfs_lfr")
            # min in lfr and max in hfr
            # min and max of combined lft and hfr contained in give wavelength range
            if a.Wavelength(RECEIVER_FREQUENCIES["rfs_lfr"].min, RECEIVER_FREQUENCIES["rfs_hfr"].max) in wavelength:
                receivers = ["rfs_lfr", "rfs_hfr"]
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
                urlpattern = self.baseurl.format(Wavelength=receiver, year=year)
                scraper = Scraper(urlpattern, regex=True)
                filesmeta = scraper._extract_files_meta(tr, extractor=self.pattern)
                for i in filesmeta:
                    rowdict = self.post_search_hook(i, matchdict)
                    metalist.append(rowdict)

        return QueryResponse(metalist, client=self)

    def post_search_hook(self, exdict, matchdict):
        """
        This method converts 'rfs_hfr' and 'rfs_lfr' in the url's metadata to the frequency ranges.

        of for low and high frequency receivers.
        """
        rowdict = super().post_search_hook(exdict, matchdict)
        if rowdict["Wavelength"] == "rfs_hfr":
            fr = RECEIVER_FREQUENCIES["rfs_hfr"]
            rowdict["Wavelength"] = u.Quantity([float(fr.min.value), float(fr.max.value)], unit=fr.unit)
        elif rowdict["Wavelength"] == "rfs_lfr":
            fr = RECEIVER_FREQUENCIES["rfs_lfr"]
            rowdict["Wavelength"] = u.Quantity([float(fr.min.value), float(fr.max.value)], unit=fr.unit)
        return rowdict

    @classmethod
    def register_values(cls):
        adict = {
            a.Instrument: [("RFS", ("Radio Frequency Spectrometer"))],
            a.Source: [("PSP", "Parker Solar Probe")],
            a.Provider: [("SPDF", "NASA Goddard Space Physics Data Facility")],
            a.Wavelength: [("*")],
        }
        return adict
