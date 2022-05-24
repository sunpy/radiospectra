import astropy.units as u
from sunpy.net import attrs as a
from sunpy.net.attr import SimpleAttr
from sunpy.net.dataretriever.client import GenericClient

from radiospectra.net.attrs import Observatory


class CALLISTOClient(GenericClient):
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
    3 Results from the CALLISTOClient:
           Start Time               End Time         Provider ... Observatory  ID
    ----------------------- ----------------------- --------- ... ----------- ---
    2019-10-05 23:00:00.000 2019-10-05 23:14:59.999 ECALLISTO ...      ALASKA  59
    2019-10-05 23:15:00.000 2019-10-05 23:29:59.999 ECALLISTO ...      ALASKA  59
    2019-10-05 23:30:00.000 2019-10-05 23:44:59.999 ECALLISTO ...      ALASKA  59
    <BLANKLINE>
    <BLANKLINE>
    """

    baseurl = (
        r"http://soleil80.cs.technik.fhnw.ch/solarradio/data/2002-20yy_Callisto/"
        r"%Y/%m/%d/{obs}_%Y%m%d_%H%M%S_(\d){{2}}.fit.gz"
    )
    pattern = (
        r"{}/2002-20yy_Callisto/{year:4d}/{month:2d}/{day:2d}/"
        r"{Observatory}_{year:4d}{month:2d}{day:2d}"
        r"_{hour:2d}{minute:2d}{second:2d}_{ID:2d}.fit.gz"
    )

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
        # Files are 15 minute duration
        original["End Time"] = original["Start Time"] + (15 * u.min - 1 * u.ms)
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
        Method the `sunpy.net.fido_factory.UnifiedDownloaderFactory` class uses to dispatch queries.

        to this Client.
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
