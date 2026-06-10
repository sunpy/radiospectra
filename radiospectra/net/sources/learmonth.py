from sunpy.net import attrs as a
from sunpy.net.dataretriever.client import GenericClient

from radiospectra.net.attrs import Observatory

__all__ = ["LearmonthClient"]


class ASWSClient(GenericClient):
    """
    Provides access to Learmonth Solar Observatory dynamic spectra
    (SRS format) hosted at the Australian Bureau of Meteorology
    `Space Weather Services <https://downloads.sws.bom.gov.au/wdc/wdc_spec/data/learmonth/raw/>`__
    World Data Centre archive.

    Learmonth is part of the RSTN network, so this client uses the same
    ``Instrument('RSTN')`` / ``Observatory('Learmonth')`` query convention as
    `~radiospectra.net.sources.rstn.RSTNClient`. The two clients differ by
    ``Provider``: ``'RSTN'`` for the NOAA NGDC mirror (pre-2019) and
    ``'SWS'`` for the actively-updated SWS archive served here.

    Examples
    --------
    >>> from radiospectra import net
    >>> from sunpy.net import Fido, attrs as a
    >>> query = Fido.search(a.Time('2017/09/06 00:00', '2017/09/06 23:59'),
    ...                     a.Instrument('Learmonth'))  #doctest: +REMOTE_DATA
    >>> query  #doctest: +REMOTE_DATA
    <sunpy.net.fido_factory.UnifiedResponse object at ...>
    Results from 1 Provider:
    <BLANKLINE>
    1 Results from the LearmonthClient:
           Start Time               End Time        Instrument Source Provider
    ----------------------- ----------------------- ---------- ------ --------
    2017-09-06 00:00:00.000 2017-09-06 23:59:59.999  LEARMONTH    SWS      SWS
    <BLANKLINE>
    <BLANKLINE>
    """

    pattern = (
        r"https://downloads.sws.bom.gov.au/wdc/wdc_spec/data/learmonth/raw/"
        r"{{year:2d}}/LM{{year:2d}}{{month:2d}}{{day:2d}}.srs"
    )

    def post_search_hook(self, exdict, matchdict):
        exdict = dict(exdict)
        exdict["year"] = int(exdict["year"]) + 2000
        rowdict = super().post_search_hook(exdict, matchdict)
        rowdict["Observatory"] = "Learmonth"
        return rowdict

    @classmethod
    def register_values(cls):
        adict = {
            a.Provider: [("SWS", "Australian Bureau of Meteorology Space Weather Services.")],
            a.Instrument: [("RSTN", "Radio Solar Telescope Network.")],
            Observatory: [("Learmonth", "Learmonth Solar Observatory.")],
        }
        return adict
