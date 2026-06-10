from sunpy.net import attrs as a
from sunpy.net.dataretriever.client import GenericClient
from astropy.time import Time 
import datetime

__all__ = ["LearmonthClient"]


class LearmonthClient(GenericClient):
    """
    Provides access to Learmonth Solar Observatory dynamic spectra
    (SRS format) hosted at the Australian Bureau of Meteorology
    `Space Weather Services <https://downloads.sws.bom.gov.au/wdc/wdc_spec/data/learmonth/raw/>`__
    World Data Centre archive.

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
        """
        The filename only carries a two-digit year, so the scraper's
        ``get_timerange_from_exdict`` would otherwise build a ``Time`` with
        year ``YY`` AD (triggering an ERFA "dubious year" warning).
        Promote the year to ``20YY`` before delegating to the parent, which
        then constructs ``Start Time`` / ``End Time`` correctly as
        labelled-date midnight-to-end-of-day nominal bounds.
        """
        exdict = dict(exdict)
        exdict["year"] = int(exdict["year"]) + 2000
        return super().post_search_hook(exdict, matchdict)


    @classmethod
    def register_values(cls):
        adict = {
            a.Instrument: [("Learmonth", "Learmonth Solar Observatory.")],
            a.Source: [("Learmonth", "Learmonth Solar Observatory.")],
            a.Provider: [("SWS", "Australian Bureau of Meteorology Space Weather Services.")],
        }
        return adict
