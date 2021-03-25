import astropy.units as u
from sunpy.net import attrs as a
from sunpy.net.attr import SimpleAttr
from sunpy.net.dataretriever.client import GenericClient


class Observatory(SimpleAttr):
    """
    Observatory
    """


class CALLISTOClient(GenericClient):
    """
    e-Callisto client

    For further information see http://www.e-callisto.org

    Notes
    -----
    For specific information on the meaning of the filename in particualr the ID field please
    see http://soleil.i4ds.ch/solarradio/data/readme.txt

    """
    baseurl = r'http://soleil80.cs.technik.fhnw.ch/solarradio/data/2002-20yy_Callisto/' \
              r'%Y/%m/%d/{obs}_%Y%m%d_%H%M%S_(\d){{2}}.fit.gz'
    pattern = r'{}/2002-20yy_Callisto/{year:4d}/{month:2d}/{day:2d}/' \
              r'{Observatory}_{year:4d}{month:2d}{day:2d}' \
              r'_{hour:2d}{minute:2d}{second:2d}_{ID:2d}.fit.gz'

    @classmethod
    def pre_search_hook(cls, *args, **kwargs):

        baseurl, pattern, matchdict = super().pre_search_hook(*args, **kwargs)
        obs = matchdict.pop('Observatory')
        if obs[0] == '*':
            baseurl = baseurl.format(obs=r'.*')
        else:
            # Need case sensitive so have to override
            obs_attr = [a for a in args if isinstance(a, Observatory)][0]
            baseurl = baseurl.format(obs=obs_attr.value)
        return baseurl, pattern, matchdict

    def post_search_hook(self, exdict, matchdict):
        original = super().post_search_hook(exdict, matchdict)
        # Files are 15 minute duration
        original['End Time'] = original['Start Time'] + (15 * u.min - 1 * u.ms)
        return original

    @classmethod
    def register_values(cls):
        adict = {
            a.Provider: [('eCALLISTO', 'International Network of Solar Radio Spectrometers.')],
            a.Instrument: [('eCALLISTO',
                            'e-Callisto - International Network of Solar Radio Spectrometers.')],
            Observatory: [('*', 'Observatory Location')]}

        return adict
