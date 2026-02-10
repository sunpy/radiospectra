from sunpy.net import attrs as a
from sunpy.net.attr import SimpleAttr
from sunpy.net.dataretriever.client import GenericClient, QueryResponse
from sunpy.net.scraper import Scraper
from sunpy.time import TimeRange

from radiospectra.net.attrs import Observatory


class eCALLISTOClient(GenericClient):
    """
    Provides access to `eCallisto radio spectrometer <http://soleil80.cs.technik.fhnw.ch/solarradio/data/2002-20yy_Callisto/>`__
    `data archive <https://spdf.gsfc.nasa.gov>`__.

    `Further information <http://www.e-callisto.org>`__.

    Notes
    -----
    `Specific information on the meaning of the filename. <http://soleil.i4ds.ch/solarradio/data/readme.txt>`__

    From the filename alone there's no way to tell about either the frequency or duration.
    Therefore we only return a start time.

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

    baseurl = (
        r"http://soleil80.cs.technik.fhnw.ch/solarradio/data/2002-20yy_Callisto/"
        r"%Y/%m/%d/{obs}_%Y%m%d_%H%M%S.*.fit.gz"
    )
    pattern = (
        r"{}/2002-20yy_Callisto/{year:4d}/{month:2d}/{day:2d}/"
        r"{Observatory}_{year:4d}{month:2d}{day:2d}"
        r"_{hour:2d}{minute:2d}{second:2d}{suffix}.fit.gz"
    )

    @classmethod
    def pre_search_hook(cls, *args, **kwargs):
        baseurl, pattern, matchdict = super().pre_search_hook(*args, **kwargs)
        obs = matchdict["Observatory"]
        if obs == "*" or obs == ["*"]:
            # Use {{obs}} (double braces) so Scraper.format() produces {obs} for parsing
            baseurl = baseurl.format(obs="{{obs}}")
        else:
            # Need case sensitive so have to override
            obs_attr = [a for a in args if isinstance(a, Observatory)][0]
            baseurl = baseurl.format(obs=obs_attr.value)
        return baseurl, pattern, matchdict

    def search(self, *args, **kwargs):
        baseurl, pattern, matchdict = self.pre_search_hook(*args, **kwargs)
        metalist = []

        # Use baseurl (which is already formatted with obs).
        # Convert to parse syntax (curly braces) for Scraper.
        # {suffix} captures user-defined suffix (was .*) - parse matches until next literal (.fit.gz)
        # Double braces {{ }} are needed because Scraper.format() consumes one level.
        pat = baseurl
        pat = pat.replace(".*", r"{{suffix}}")
        pat = pat.replace("%Y%m%d", r"{{year:4d}}{{month:2d}}{{day:2d}}")
        pat = pat.replace("%H%M%S", r"{{hour:2d}}{{minute:2d}}{{second:2d}}")
        pat = pat.replace("%Y", r"{{year:4d}}")
        pat = pat.replace("%m", r"{{month:2d}}")
        pat = pat.replace("%d", r"{{day:2d}}")

        scraper = Scraper(pat)
        tr = TimeRange(matchdict["Start Time"], matchdict["End Time"])

        # If wildcard, remove Observatory from matcher to avoid Scraper filtering it out
        # (Scraper compares 'ALASKA' with ['*'])
        matcher = matchdict.copy()
        if matcher.get("Observatory") == ["*"] or matcher.get("Observatory") == "*":
            del matcher["Observatory"]

        filesmeta = scraper._extract_files_meta(tr, matcher=matcher)

        for i in filesmeta:
            rowdict = self.post_search_hook(i, matchdict)
            metalist.append(rowdict)

        return QueryResponse(metalist, client=self)

    def post_search_hook(self, exdict, matchdict):
        original = super().post_search_hook(exdict, matchdict)
        if "obs" in original:
            original["Observatory"] = original.pop("obs")

        # ID is derived from suffix.
        if "suffix" in original:
            original["ID"] = original["suffix"].replace("_", "")
            del original["suffix"]

        # We don't know the end time for all files
        # https://github.com/sunpy/radiospectra/issues/60
        del original["End Time"]
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
