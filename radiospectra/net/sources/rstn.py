from sunpy.net import attrs as a
from sunpy.net.dataretriever.client import GenericClient, QueryResponse
from sunpy.net.scraper import Scraper
from sunpy.time.timerange import TimeRange

from radiospectra.net.attrs import Observatory

__all__ = ["RSTNClient"]


class RSTNClient(GenericClient):
    """
    Radio Spectrometer Telescope Network (RSTN) hosted at NOAA
    `National Geophysical Data <https://www.ngdc.noaa.gov>`__ (NGDC) archive.

    Examples
    --------
    >>> from radiospectra import net
    >>> from sunpy.net import Fido, attrs as a
    >>> query = Fido.search(a.Time('2003/03/15 00:00', '2003/03/15 23:59'),
    ...                     a.Instrument('RSTN'), net.Observatory('San Vito'))  #doctest: +REMOTE_DATA
    >>> query  #doctest: +REMOTE_DATA
    <sunpy.net.fido_factory.UnifiedResponse object at ...
    Results from 1 Provider:
    <BLANKLINE>
    1 Results from the RSTNClient:
    2003-03-15 00:00:00.000 2003-03-15 23:59:59.999     RSTN       RSTN    San Vito
    <BLANKLINE>
    <BLANKLINE>
    """

    baseurl = (
        r"https://www.ngdc.noaa.gov/stp/space-weather/solar-data/"
        r"solar-features/solar-radio/rstn-spectral/{obs}/%Y/%m/.*.gz"
    )
    pattern = r"{}/rstn-spectral/{obs}/{year:4d}/{month:2d}/" r"{obs_short:2l}{year2:2d}{month2:2d}{day:2d}.SRS.gz"

    observatory_map = {
        "Holloman": "holloman",
        "Learmonth": "learmonth",
        "Palehua": "palehua",
        "Sagamore Hill": "sagamore",
        "San Vito": "san-vito",
    }
    observatory_map = {**observatory_map, **dict(map(reversed, observatory_map.items()))}

    def search(self, *args, **kwargs):
        baseurl, pattern, matchdict = self.pre_search_hook(*args, **kwargs)
        metalist = []
        for obs in matchdict["Observatory"]:
            # Construct pattern template for Scraper
            # baseurl is like .../rstn-spectral/{obs}/...
            # pattern is {}/rstn-spectral/{obs}/...
            # Resolve {} and {obs}
            domain = baseurl.split("/rstn-spectral")[0]
            obs_norm = self.observatory_map[obs.title()]

            # Construct regex pattern for Scraper
            # Use SunPy 'parse' syntax (curly braces) which Scraper expects.
            # Double braces {{ }} are needed for Scraper.format().
            # Quadruple braces {{{{ }}}} are needed for Python f-string escaping.
            # Filename matching uses strict format.
            pat = f"{domain}/rstn-spectral/{obs_norm}/{{{{year:4d}}}}/{{{{month:2d}}}}/{{{{obs_short}}}}{{{{year:2d}}}}{{{{month:2d}}}}{{{{day:2d}}}}.SRS.gz"

            scraper = Scraper(pat)
            tr = TimeRange(matchdict["Start Time"], matchdict["End Time"])
            filesmeta = scraper._extract_files_meta(tr)

            for i in filesmeta:
                rowdict = self.post_search_hook(i, matchdict)
                # Ensure Title Case for Observatory name (e.g. San Vito)
                # Obs might be 'san vito' or 'san-vito'. Map handles hyphenated.
                # .title() handles checking space-separated.
                mapped = self.observatory_map.get(obs, obs)
                rowdict["Observatory"] = mapped if mapped != obs else obs.title()
                metalist.append(rowdict)

        return QueryResponse(metalist, client=self)

    def post_search_hook(self, exdict, matchdict):
        original = super().post_search_hook(exdict, matchdict)
        original.pop("obs_short", None)
        return original

    @classmethod
    def register_values(cls):
        adict = {
            a.Provider: [("RSTN", "Radio Solar Telescope Network.")],
            a.Instrument: [("RSTN", "Radio Solar Telescope Network.")],
            Observatory: [
                ("Holloman", "Holloman"),
                ("Learmonth", "Learmonth"),
                ("Palehua", "Palehua"),
                ("Sagamore Hill", "Sagamore Hill"),
                ("San Vito", "San Vito"),
            ],
        }
        return adict
