from sunpy.net import attrs as a
from sunpy.net.dataretriever.client import GenericClient

from radiospectra.net.attrs import PolType


class EOVSAClient(GenericClient):
    """
    Provides access to `Extended Owens Valley Solar Array <http://www.ovsa.njit.edu>`__ (EOVSA) data.

    Examples
    --------
    >>> from radiospectra import net
    >>> from sunpy.net import Fido, attrs as a
    >>> query = Fido.search(a.Time('2020/10/05 00:00', '2020/10/06 00:00'),
    ...                     a.Instrument('EOVSA'), net.PolType.cross)  #doctest: +REMOTE_DATA
    >>> query  #doctest: +REMOTE_DATA
    <sunpy.net.fido_factory.UnifiedResponse object at ...>
    Results from 1 Provider:
    <BLANKLINE>
    2 Results from the EOVSAClient:
           Start Time               End Time        Provider Instrument PolType
    ----------------------- ----------------------- -------- ---------- -------
    2020-10-05 00:00:00.000 2020-10-05 23:59:59.999    EOVSA      EOVSA   Cross
    2020-10-06 00:00:00.000 2020-10-06 23:59:59.999    EOVSA      EOVSA   Cross
    <BLANKLINE>
    <BLANKLINE>
    """

    baseurl = r"http://ovsa.njit.edu/fits/synoptic/%Y/%m/%d/" r"EOVSA_.*_%Y%m%d.fts"
    pattern = r"{}/synoptic/{year:4d}/{month:2d}/{day:2d}/" r"EOVSA_{PolType:5l}_{year:4d}{month:2d}{day:2d}.fts"

    pol_map = {"Total": "TPall", "Cross": "XPall", "TPall": "Total", "XPall": "Cross"}

    @classmethod
    def pre_search_hook(cls, *args, **kwargs):
        baseurl, pattern, matchdict = super().pre_search_hook(*args, **kwargs)
        pol_values = [cls.pol_map[p.capitalize()] for p in matchdict["PolType"]]
        matchdict["PolType"] = pol_values
        return baseurl, pattern, matchdict

    def post_search_hook(self, exdict, matchdict):
        original = super().post_search_hook(exdict, matchdict)
        original["PolType"] = self.pol_map[original["PolType"]]
        return original

    @classmethod
    def register_values(cls):
        adict = {
            a.Provider: [("EOVSA", "EOVSA")],
            a.Instrument: [("EOVSA", "ExtendedOwens Valley Solar Array.")],
            PolType: [("Total", "Total polarisation"), ("Cross", "Cross polarisation")],
        }
        return adict
