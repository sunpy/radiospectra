from typing import Any, cast
from datetime import datetime
from collections import OrderedDict

from astropy.time import Time

from sunpy.net import attrs as a
from sunpy.net.dataretriever import GenericClient

__all__ = ["NDAClient"]


class NDAClient(GenericClient):  # type: ignore[misc]
    """
    Client for Nançay Decameter Array (NDA) solar radio observations.

    This client searches data in the ``NewRoutine`` format available here:
    https://cdn.obs-nancay.fr/repository/nda/newroutine/soleil/

    Data source:
    https://cdn.obs-nancay.fr/repository/nda/newroutine/soleil/

    Examples
    --------
    >>> from radiospectra import net
    >>> from sunpy.net import Fido, attrs as a
    >>> query = Fido.search(
    ...     a.Time("2025-03-26", "2025-03-27"),
    ...     a.Instrument("NDA")) #doctest: +REMOTE_DATA
    >>> query #doctest: +REMOTE_DATA
    <sunpy.net.fido_factory.UnifiedResponse object at ...>
    Results from 1 Provider:
    <BLANKLINE>
    1 Results from the NDAClient:
    Source: https://cdn.obs-nancay.fr/repository/nda/newroutine/soleil/
    <BLANKLINE>
        Start Time             End Time      Instrument  Physobs    Provider Source Version
    ----------------------- ------------------- ---------- ---------- --------- ------ -------
    2025-03-26 07:56:00.000 2025-03-26 15:55:00        NDA radio_flux OBSNANCAY    NDA     1.1
    <BLANKLINE>
    <BLANKLINE>
    """

    pattern = (
        "https://cdn.obs-nancay.fr/repository/nda/newroutine/soleil/"
        "{{year:4d}}/{{month:2d}}/orn_nda_newroutine_sun_edr_"
        "{{year:4d}}{{month:2d}}{{day:2d}}{{hour:2d}}{{minute:2d}}_"
        "{{end_year:4d}}{{end_month:2d}}{{end_day:2d}}{{end_hour:2d}}{{end_minute:2d}}_v{{version}}.fits"
    )

    @property
    def info_url(self) -> str:
        return "https://cdn.obs-nancay.fr/repository/nda/newroutine/soleil/"

    @classmethod
    def register_values(cls) -> dict[Any, object]:
        return {
            a.Instrument: [("NDA", "Nançay Decameter Array")],
            a.Physobs: [("radio_flux", "Solar radio flux density")],
            a.Provider: [("ObsNancay", "Observatoire de Nançay")],
            a.Source: [("NDA", "Nançay Data Center")],
        }

    def post_search_hook(self, exdict: dict[str, Any], matchdict: dict[str, Any]) -> OrderedDict[str, Any]:
        rowdict = cast(OrderedDict[str, Any], super().post_search_hook(exdict, matchdict))

        # Fix End Time from filename (important correction)
        year, month, day, hour, minute = (
            int(exdict.pop(f"end_{p}")) for p in ("year", "month", "day", "hour", "minute")
        )
        rowdict["End Time"] = Time(datetime(year, month, day, hour, minute))
        rowdict["Version"] = rowdict["version"][:]

        # Clean up helper fields
        for key in ("end_year", "end_month", "end_day", "end_hour", "end_minute", "version"):
            rowdict.pop(key, None)

        return rowdict
