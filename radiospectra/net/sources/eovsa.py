from sunpy.net import attrs as a
from sunpy.net.attr import SimpleAttr
from sunpy.net.dataretriever.client import GenericClient


class PolType(SimpleAttr):
    pass


class EOVSAClient(GenericClient):
    """
    e-Callisto client

    For further information see http://www.e-callisto.org

    Notes
    -----
    For specific information on the meaning of the filename in particualr the ID field please
    see http://soleil.i4ds.ch/solarradio/data/readme.txt

    """
    baseurl = r'http://ovsa.njit.edu/fits/synoptic/%Y/%m/%d/' \
              r'EOVSA_.*_%Y%m%d.fts'
    pattern = r'{}/synoptic/{year:4d}/{month:2d}/{day:2d}/' \
              r'EOVSA_{PolType:5l}_{year:4d}{month:2d}{day:2d}.fts'

    pol_map = {
        'Total': 'TPall',
        'Cross': 'XPall',
        'TPall': 'Total',
        'XPall': 'Cross'
    }

    @classmethod
    def pre_search_hook(cls, *args, **kwargs):
        baseurl, pattern, matchdict = super().pre_search_hook(*args, **kwargs)
        pol_values = [cls.pol_map[p.capitalize()] for p in matchdict['PolType']]
        matchdict['PolType'] = pol_values
        return baseurl, pattern, matchdict

    def post_search_hook(self, exdict, matchdict):
        original = super().post_search_hook(exdict, matchdict)
        original['PolType'] = self.pol_map[original['PolType']]
        return original

    @classmethod
    def register_values(cls):
        adict = {
            a.Provider: [('EOVSA', 'EOVSA')],
            a.Instrument: [('EOVSA',
                            'ExtendedOwens Valley Solar Array.')],
            PolType: [('Total', 'Total polarisation'),
                      ('Cross', 'Cross polarisation')]}
        return adict
