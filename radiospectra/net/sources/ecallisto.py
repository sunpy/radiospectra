from sunpy.net import attrs as a
from sunpy.net.attr import SimpleAttr
from sunpy.net.dataretriever.client import GenericClient

from radiospectra.net.attrs import Observatory


class eCALLISTOClient(GenericClient):
    """
    Provides access to `eCallisto radio spectrometer <http://soleil80.cs.technik.fhnw.ch/solarradio/data/2002-20yy_Callisto/>`__
    `data archive <https://spdf.gsfc.nasa.gov>`__.

    `Further information <http://www.e-callisto.org>`__.

    Notes
    -----
    `Specific information on the meaning of the filename. <http://soleil.i4ds.ch/solarradio/data/readme.txt>`__

    Examples
    --------
    >>> from radiospectra import net
    >>> from sunpy.net import Fido, attrs as a
    >>> query = Fido.search(a.Time('2019/10/05 23:00', '2019/10/05 23:30'),
    ...                     a.Instrument('eCALLISTO'), net.Observatory('ALASKA'))  #doctest: +REMOTE_DATA
    >>> query  #doctest: +REMOTE_DATA
    <sunpy.net.fido_factory.UnifiedResponse object at ...>
    Results from 1 Provider:
    <BLANKLINE>
    3 Results from the eCALLISTOClient:
           Start Time        Provider Instrument Observatory  ID
    ----------------------- --------- ---------- ----------- ---
    2019-10-05 23:00:00.000 ECALLISTO  ECALLISTO      ALASKA  59
    2019-10-05 23:15:00.000 ECALLISTO  ECALLISTO      ALASKA  59
    2019-10-05 23:30:00.000 ECALLISTO  ECALLISTO      ALASKA  59
    <BLANKLINE>
    <BLANKLINE>
    """
    baseurl = r'http://soleil80.cs.technik.fhnw.ch/solarradio/data/2002-20yy_Callisto/' \
              r'%Y/%m/%d/{obs}_%Y%m%d_%H%M%S.*.fit.gz'
    pattern = r'{}/2002-20yy_Callisto/{year:4d}/{month:2d}/{day:2d}/' \
              r'{Observatory}_{year:4d}{month:2d}{day:2d}' \
              r'_{hour:2d}{minute:2d}{second:2d}{suffix}.fit.gz'

    @classmethod
    def pre_search_hook(cls, *args, **kwargs):
        baseurl, pattern, matchdict = super().pre_search_hook(*args, **kwargs)
        obs = matchdict.pop("Observatory")
        if obs[0] == "*":
            baseurl = baseurl.format(obs=r".*")
        else:
            # Need case sensitive so have to override
            obs_attr = [a for a in args if isinstance(a, Observatory)][0]
            baseurl = baseurl.format(obs=obs_attr.value)
        return baseurl, pattern, matchdict

    def post_search_hook(self, exdict, matchdict):
        original = super().post_search_hook(exdict, matchdict)
        i0 = 0
        if '_' in original['suffix']:
            i0 = 1
        original['ID'] = original['suffix'][i0:]
        del original['suffix']
        # Don't know the end time for all files see https://github.com/sunpy/radiospectra/issues/60
        del original['End Time']

        return original

    @classmethod
    def register_values(cls):
        adict = {
            a.Provider: [("eCALLISTO", "International Network of Solar Radio Spectrometers.")],
            a.Instrument: [("eCALLISTO", "e-Callisto - International Network of Solar Radio Spectrometers.")],
            Observatory: [("*", "Observatory Location")],
        }
        return adict

    @classmethod
    def _can_handle_query(cls, *query):
        """
        Method the `sunpy.net.fido_factory.UnifiedDownloaderFactory` class uses
        to dispatch queries to this Client.
        """
        regattrs_dict = cls.register_values()
        optional = {k for k in regattrs_dict.keys()} - cls.required
        if not cls.check_attr_types_in_query(query, cls.required, optional):
            return False
        for key in regattrs_dict:
            all_vals = [i[0].lower() for i in regattrs_dict[key]]
            for x in query:
                if (
                    isinstance(x, key)
                    and issubclass(key, SimpleAttr)
                    and x.type_name != "observatory"
                    and str(x.value).lower() not in all_vals
                ):
                    return False
        return True
