from sunpy.net import attrs as a
from sunpy.net.attr import SimpleAttr
from sunpy.net.dataretriever.client import GenericClient

from radiospectra.net.attrs import Observatory
import zlib
import urllib.request
import urllib.error
import logging
from astropy.io import fits
from astropy.time import Time

log = logging.getLogger(__name__)

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

    pattern = (
        r"http://soleil80.cs.technik.fhnw.ch/solarradio/data/2002-20yy_Callisto/"
        r"{year:4d}/{month:2d}/{day:2d}/{obs}_{year:4d}{month:2d}{day:2d}"
        r"_{hour:2d}{minute:2d}{second:2d}{suffix}.fit.gz"
    )

    @classmethod
    def pre_search_hook(cls, *args, **kwargs):
        baseurl, pattern, matchdict = super().pre_search_hook(*args, **kwargs)
        obs = matchdict["Observatory"]
        if obs[0] == "*":
            pattern = pattern.replace("{obs}", "{Observatory}")
            matchdict.pop("Observatory")
        else:
            
            obs_attr = [a for a in args if isinstance(a, Observatory)][0]
            pattern = pattern.replace("{obs}", obs_attr.value)
        return baseurl, pattern, matchdict

    def post_search_hook(self, exdict, matchdict):
        original = super().post_search_hook(exdict, matchdict)
        original["ID"] = original["suffix"].replace("_", "")
        del original["suffix"]
        url = exdict.get('url')
        if url:
            start_h, end_h = self._fetch_remote_header(url)
            if start_h:
                try:
                    original["Start Time"] = Time(start_h)
                except (ValueError, TypeError):
                    pass

            if end_h:
                try:
                    original["End Time"] = Time(end_h)
                except (ValueError, TypeError):
                    original["End Time"] = end_h
            else:
                if "End Time" in original:
                    del original["End Time"]            
        else:
            if "End Time" in original:
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
    
    def _fetch_remote_header(self, url):
        headers = {'User-Agent': 'SunPy/Radiospectra', 'Range': 'bytes=0-15360'}
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.getcode() == 206:
                    compressed_data = response.read()
                    # e-Callisto files are .gz, so we need to decompress
                    d = zlib.decompressobj(16 + zlib.MAX_WBITS)
                    header_bytes = d.decompress(compressed_data)
                    header = fits.Header.fromstring(header_bytes[:2880].decode('ascii', errors='ignore'))

                    # Get Date and Time keywords
                    date_obs = header.get('DATE-OBS')
                    time_obs = header.get('TIME-OBS', '')
                    date_end = header.get('DATE-END', date_obs)
                    time_end = header.get('TIME-END', '')

                    # Combine into strings for Astropy Time
                    start = f"{date_obs} {time_obs}".strip()
                    end = f"{date_end} {time_end}".strip()

                    return (start if date_obs else None), (end if date_end else None)
                
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            log.warning(f"Network error fetching e-Callisto header from {url}: {e}")
        except (zlib.error, ValueError, KeyError) as e:
            log.warning(f"Metadata parsing error for {url}: {e}")

        return None, None