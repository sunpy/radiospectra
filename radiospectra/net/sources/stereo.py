from itertools import product

import astropy.units as u
from sunpy.net import attrs as a
from sunpy.net.dataretriever.client import GenericClient, QueryResponse
from sunpy.net.scraper import Scraper
from sunpy.time import TimeRange

from radiospectra.net import attrs as ra

__all__ = ["SWAVESClient"]


RECEIVER_FREQUENCIES = {
    "lfr": a.Wavelength(10 * u.kHz, 160 * u.kHz),
    "hfr": a.Wavelength(0.125 * u.MHz, 16 * u.MHz),
}


class SWAVESClient(GenericClient):
    """
    Provides access to `STEREO S-WAVES <https://swaves.gsfc.nasa.gov/swaves_instr.html>`__ radio.

    `data archive <https://solar-radio.gsfc.nasa.gov/data/stereo>`__.

    Examples
    --------
    >>> import radiospectra.net
    >>> from sunpy.net import Fido, attrs as a
    >>> results = Fido.search(a.Time("2010/10/01", "2010/10/02"),
    ...                       a.Instrument('SWAVES'))  # doctest: +REMOTE_DATA
    >>> results[1] #doctest: +REMOTE_DATA
    <sunpy.net.dataretriever.client.QueryResponse object at ...>
           Start Time               End Time        ... Provider    Wavelength
                                                    ...                kHz
    ----------------------- ----------------------- ... -------- ----------------
    2010-10-01 00:00:00.000 2010-10-01 23:59:59.999 ...     NASA    10.0 .. 160.0
    2010-10-02 00:00:00.000 2010-10-02 23:59:59.999 ...     NASA    10.0 .. 160.0
    2010-10-01 00:00:00.000 2010-10-01 23:59:59.999 ...     NASA 125.0 .. 16000.0
    2010-10-02 00:00:00.000 2010-10-02 23:59:59.999 ...     NASA 125.0 .. 16000.0
    2010-10-01 00:00:00.000 2010-10-01 23:59:59.999 ...     NASA    10.0 .. 160.0
    2010-10-02 00:00:00.000 2010-10-02 23:59:59.999 ...     NASA    10.0 .. 160.0
    2010-10-01 00:00:00.000 2010-10-01 23:59:59.999 ...     NASA 125.0 .. 16000.0
    2010-10-02 00:00:00.000 2010-10-02 23:59:59.999 ...     NASA 125.0 .. 16000.0
    """

    baseurl = (
        r"https://solar-radio.gsfc.nasa.gov/data/stereo/summary/{year}/"
        r"swaves_average_(\d){{8}}_{Spacecraft}_{Wavelength}.dat"
    )

    pattern = r"{}/{year:4d}/" r"swaves_average_{year:4d}{month:2d}{day:2d}_{Spacecraft}_{Wavelength}.dat"

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
            if wavelength.min in RECEIVER_FREQUENCIES["hfr"] or wavelength.max in RECEIVER_FREQUENCIES["hfr"]:
                receivers.append("hfr")
            if wavelength.min in RECEIVER_FREQUENCIES["lfr"] or wavelength.max in RECEIVER_FREQUENCIES["lfr"]:
                receivers.append("lfr")
            # min in lfr and max in hfr
            # min and max of combined lft and hfr contained in give wavelength range
            if a.Wavelength(RECEIVER_FREQUENCIES["lfr"].min, RECEIVER_FREQUENCIES["hfr"].max) in wavelength:
                receivers = ["lfr", "hfr"]
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

        spacecraft = matchdict.get("spacecraft", ["a", "b"])

        metalist = []
        start_year = matchdict["Start Time"].datetime.year
        end_year = matchdict["End Time"].datetime.year
        tr = TimeRange(matchdict["Start Time"], matchdict["End Time"])
        for spc, receiver in product(spacecraft, receivers):
            for year in range(start_year, end_year + 1):
                urlpattern = self.baseurl.format(Wavelength=receiver, Spacecraft=spc, year=year)
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
        if rowdict["Wavelength"] == "hfr":
            fr = RECEIVER_FREQUENCIES["hfr"]
            rowdict["Wavelength"] = u.Quantity([float(fr.min.value), float(fr.max.value)], unit=fr.unit)
        elif rowdict["Wavelength"] == "lfr":
            fr = RECEIVER_FREQUENCIES["lfr"]
            rowdict["Wavelength"] = u.Quantity([float(fr.min.value), float(fr.max.value)], unit=fr.unit)
        return rowdict

    @classmethod
    def register_values(cls):
        adict = {
            a.Instrument: [("SWAVES", "STEREO WAVES - SWAVES")],
            a.Source: [("STEREO", "Solar Terrestrial Relations Observatory")],
            ra.Spacecraft: [("A", "Ahead"), ("B", "Behind")],
            a.Provider: [("NASA", "NASA Goddard Space Flight Center")],
            a.Wavelength: [("*")],
        }
        return adict
