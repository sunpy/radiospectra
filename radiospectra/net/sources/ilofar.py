import astropy.units as u
from sunpy.net import attrs as a
from sunpy.net.dataretriever.client import GenericClient, QueryResponse
from sunpy.time import TimeRange
from sunpy.util.scraper import Scraper

__all__ = ['ILOFARClient']


RECEIVER_FREQUENCIES = {
    'rad1': a.Wavelength(20*u.kHz, 1040*u.kHz),
    'rad2': a.Wavelength(1.075*u.MHz, 13.825*u.MHz),
}

RECEIVER_EXT = {
    'rad1': 'R1',
    'rad2': 'R2',
}


class ILOFARClient(GenericClient):
    """
    Provides access to I-LOFAR mode 357 observations from the
    data `archive <https://data.lofar.ie>`__

    Examples
    --------
    >>> import radiospectra.net
    >>> from sunpy.net import Fido, attrs as a
    >>> results = Fido.search(a.Time("2010/10/01", "2010/10/02"),
    ...                       a.Instrument('WAVES'))  # doctest: +REMOTE_DATA
    >>> results #doctest: +REMOTE_DATA
    <sunpy.net.fido_factory.UnifiedResponse object at...>
    Results from 1 Provider:
    <BLANKLINE>
    4 Results from the WAVESClient:
           Start Time               End Time        ... Provider   Wavelength [2]
                                                    ...                 kHz
    ----------------------- ----------------------- ... -------- -----------------
    2010-10-01 00:00:00.000 2010-10-01 23:59:59.999 ...     NASA    20.0 .. 1040.0
    2010-10-02 00:00:00.000 2010-10-02 23:59:59.999 ...     NASA    20.0 .. 1040.0
    2010-10-01 00:00:00.000 2010-10-01 23:59:59.999 ...     NASA 1075.0 .. 13825.0
    2010-10-02 00:00:00.000 2010-10-02 23:59:59.999 ...     NASA 1075.0 .. 13825.0
    <BLANKLINE>
    """

    baseurl = (r'https://data.lofar.ie/%Y/%m/%d/bst/kbt/rcu357_1beam/'
               r'%Y%m%d_\d{6}_bst_\d{2}\S{1}.dat')

    pattern = r'{}/{year:4d}{month:2d}{day:2d}_{hour:2d}{minute:2d}{second:2d}' \
              r'_bst_{num:2d}{Polarisation}.dat'

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
        tr = TimeRange(matchdict['Start Time'], matchdict['End Time'])
        scraper = Scraper(self.baseurl, regex=True)
        filesmeta = scraper._extract_files_meta(tr, extractor=self.pattern)
        for i in filesmeta:
            rowdict = self.post_search_hook(i, matchdict)
            metalist.append(rowdict)

        return QueryResponse(metalist, client=self)

    @classmethod
    def register_values(cls):
        adict = {a.Instrument: [('ILOFAR', 'Irish LOFAR STATION (IE63)')],
                 a.Source: [('ILOFAR', 'Irish LOFAR Data Archive')],
                 a.Provider: [('ILOFAR', 'Irish LOFAR Data Archive')],
                 a.Wavelength: [('*')]}
        return adict
