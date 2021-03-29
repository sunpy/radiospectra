from sunpy.net import attrs as a
from sunpy.net.attr import SimpleAttr
from sunpy.net.dataretriever.client import GenericClient, QueryResponse
from sunpy.time.timerange import TimeRange
from sunpy.util.scraper import Scraper


class Observatory(SimpleAttr):
    """
    Observatory
    """


class RSTNClient(GenericClient):
    """
    e-Callisto client

    For further information see http://www.e-callisto.org

    Notes
    -----
    For specific information on the meaning of the filename in particualr the ID field please
    see http://soleil.i4ds.ch/solarradio/data/readme.txt

    """
    baseurl = r'https://www.ngdc.noaa.gov/stp/space-weather/solar-data/' \
              r'solar-features/solar-radio/rstn-spectral/{obs}/%Y/%m/.*.gz'
    pattern = r'{}/rstn-spectral/{obs}/{year:4d}/{month:2d}/' \
              r'{obs_short:2l}{year2:2d}{month2:2d}{day:2d}.SRS.gz'

    observatory_map = {
        'Holloman': 'holloman',
        'Learmonth': 'learmonth',
        'Palehua': 'palehua',
        'Sagamore Hill': 'sagamore',
        'San Vito': 'san-vito',
    }
    observatory_map = {**observatory_map, **dict(map(reversed, observatory_map.items()))}

    def search(self, *args, **kwargs):
        baseurl, pattern, matchdict = self.pre_search_hook(*args, **kwargs)
        metalist = []
        for obs in matchdict['Observatory']:
            scraper = Scraper(baseurl.format(obs=self.observatory_map[obs.title()]), regex=True)
            tr = TimeRange(matchdict['Start Time'], matchdict['End Time'])
            filesmeta = scraper._extract_files_meta(tr, extractor=pattern,
                                                    matcher=matchdict)

            for i in filesmeta:
                rowdict = self.post_search_hook(i, matchdict)
                metalist.append(rowdict)

        return QueryResponse(metalist, client=self)

    def post_search_hook(self, exdict, matchdict):
        original = super().post_search_hook(exdict, matchdict)
        obs, *_ = [original.pop(name) for name in ['obs', 'year2', 'month2', 'obs_short']]
        original['Observatory'] = self.observatory_map[obs]
        return original

    @classmethod
    def register_values(cls):
        adict = {
            a.Provider: [('RSTN', 'Radio Solar Telescope Network.')],
            a.Instrument: [('RSTN', 'Radio Solar Telescope Network.')],
            Observatory: [('Holloman', 'Holloman'),
                          ('Learmonth', 'Learmonth'),
                          ('Palehua', 'Palehua'),
                          ('Sagamore Hill', 'Sagamore Hill'),
                          ('San Vito', 'San Vito')]}
        return adict
