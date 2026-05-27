
from datetime import datetime
from astropy.time import Time
from sunpy.net import attrs as a
from sunpy.net.dataretriever import GenericClient

__all__ = ["NDAClient"]


class NDAClient(GenericClient):
    """
    Client for NDA NewRoutine solar FITS observations.

    Data source:
    https://cdn.obs-nancay.fr/repository/nda/newroutine/soleil/

    Examples
    --------
    >>> from sunpy.net import Fido, attrs as a

    >>> results = Fido.search(
    ...     a.Time("2025-03-26", "2025-03-27"),
    ...     a.Instrument("NDA")
    ... )
    """

    pattern = (
        "https://cdn.obs-nancay.fr/"
        "repository/nda/newroutine/soleil/"
        "{{year:4d}}/"
        "{{month:2d}}/"
        "orn_nda_newroutine_sun_edr_"
        "{{year:4d}}{{month:2d}}{{day:2d}}"
        "{{hour:2d}}{{minute:2d}}_"
        "{{end_year:4d}}{{end_month:2d}}{{end_day:2d}}"
        "{{end_hour:2d}}{{end_minute:2d}}"
        "_v{{version}}.fits"
    )

    @property
    def info_url(self):
        return (
            "https://cdn.obs-nancay.fr/"
            "repository/nda/newroutine/soleil/"
        )

    @classmethod
    def register_values(cls):
        return {
            a.Instrument: [
                ("NDA", "Nançay Decameter Array")
            ],

            a.Physobs: [
                ("radio_flux", "Solar radio flux density")
            ],

            a.Provider: [
                ("ObsNancay", "Observatoire de Nançay")
            ],

            a.Source: [
                ("SUN", "Solar observations")
            ],
        }
    def post_search_hook(self, exdict, matchdict):
        rowdict = super().post_search_hook(exdict, matchdict)

        # Fix End Time from filename (important correction)
        end = Time(datetime(
            int(exdict["end_year"]),
            int(exdict["end_month"]),
            int(exdict["end_day"]),
            int(exdict["end_hour"]),
            int(exdict["end_minute"]),
        ))

        rowdict["End Time"] = end

        # Clean up helper fields
        for key in (
            "end_year",
            "end_month",
            "end_day",
            "end_hour",
            "end_minute",
            "version",
        ):
            rowdict.pop(key, None)

        return rowdict
