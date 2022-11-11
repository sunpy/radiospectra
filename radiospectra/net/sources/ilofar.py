import numpy as np

import astropy.units as u
from sunpy.net import attrs as a
from sunpy.net.dataretriever.client import GenericClient, QueryResponse
from sunpy.time import TimeRange
from sunpy.util.scraper import Scraper

from radiospectra.net.attrs import PolType

__all__ = ["ILOFARMode357Client"]

RECEIVER_FREQUENCIES = a.Wavelength(10.546875 * u.MHz, 244.53125 * u.MHz)
DATASET_NAMES = ["rcu357_1beam", "rcu357_1beam_datastream"]


class ILOFARMode357Client(GenericClient):
    """
    Provides access to I-LOFAR mode 357 observations from the
    data `archive <https://data.lofar.ie>`__

    Examples
    --------
    >>> import radiospectra.net
    >>> from sunpy.net import Fido, attrs as a
    >>> results = Fido.search(a.Time("2021/09/01", "2021/09/21"),
    ...                       a.Instrument('ILOFAR'))  # doctest: +REMOTE_DATA
    >>> results #doctest: +REMOTE_DATA
    <sunpy.net.fido_factory.UnifiedResponse object ...
    Results from 1 Provider:
    <BLANKLINE>
           Start Time               End Time        ... PolType Polarisation
    ----------------------- ----------------------- ... ------- ------------
    2021-09-14 07:39:13.000 2021-09-14 07:39:13.999 ...       X            X
    2021-09-14 07:39:13.000 2021-09-14 07:39:13.999 ...       X            Y
    2021-09-01 08:07:29.000 2021-09-01 08:07:29.999 ...       X            X
    2021-09-01 08:07:29.000 2021-09-01 08:07:29.999 ...       X            Y
    2021-09-07 08:07:52.000 2021-09-07 08:07:52.999 ...       X            X
    2021-09-07 08:07:52.000 2021-09-07 08:07:52.999 ...       X            Y
    2021-09-08 08:04:07.000 2021-09-08 08:04:07.999 ...       X            X
    2021-09-08 08:04:07.000 2021-09-08 08:04:07.999 ...       X            Y
    2021-09-08 10:34:31.000 2021-09-08 10:34:31.999 ...       X            X
    2021-09-08 10:34:31.000 2021-09-08 10:34:31.999 ...       X            Y
    <BLANKLINE>
    <BLANKLINE>
    """

    baseurl = r"https://data.lofar.ie/%Y/%m/%d/bst/kbt/{dataset}/" r"%Y%m%d_\d{{6}}_bst_00\S{{1}}.dat"

    pattern = r"{}/{year:4d}{month:2d}{day:2d}_{hour:2d}{minute:2d}{second:2d}" r"_bst_00{Polarisation}.dat"

    @classmethod
    def _check_wavelengths(cls, wavelength):
        """
        Check for overlap between given wavelength and receiver frequency coverage defined in
        `RECEIVER_FREQUENCIES`.

        Parameters
        ----------
        wavelength : `sunpy.net.attrs.Wavelength`
            Input wavelength range to check

        Returns
        -------
        `bool`
        """
        return wavelength.min in RECEIVER_FREQUENCIES or wavelength.max in RECEIVER_FREQUENCIES

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
        metalist = []

        wavelentgh = matchdict.get("Wavelength", False)
        if wavelentgh and not self._check_wavelengths(wavelentgh):
            return QueryResponse(metalist, client=self)

        tr = TimeRange(matchdict["Start Time"], matchdict["End Time"])

        for dataset in DATASET_NAMES:
            url = self.baseurl.format(dataset=dataset)
            scraper = Scraper(url, regex=True)
            filesmeta = scraper._extract_files_meta(tr, extractor=self.pattern)
            for i in filesmeta:
                rowdict = self.post_search_hook(i, matchdict)
                metalist.append(rowdict)

        query_response = QueryResponse(metalist, client=self)
        mask = np.full(len(query_response), True)
        pol = matchdict.get("PolType")
        if len(pol) == 1:
            pol = pol.upper()
            mask = mask & query_response["Polarisation"] == pol

        if query_response:
            query_response.remove_column("PolType")

        return query_response[mask]

    @classmethod
    def register_values(cls):
        adict = {
            a.Instrument: [("ILOFAR", "Irish LOFAR STATION (IE63)")],
            a.Source: [("ILOFAR", "Irish LOFAR Data Archive")],
            a.Provider: [("ILOFAR", "Irish LOFAR Data Archive")],
            a.Wavelength: [("*")],
            PolType: [("X", "X"), ("X Linear Polarisation", "Y Linear Polarisation")],
        }
        return adict
