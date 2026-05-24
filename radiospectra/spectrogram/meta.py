"""
Abstract base class for dynamic spectra
"""
import abc

from ndcube.meta import NDMeta
from sunraster.meta import MetaABC

__all__ = [
    'SpectrogramMetaABC',
    'SpectrogramMeta',
]


class SpectrogramMetaABC(MetaABC):

    @abc.abstractmethod
    def target(self):
        """The target coordinate of the observation."""
        pass


class SpectrogramMeta(NDMeta,SpectrogramMetaABC):

    _registry = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "is_datasource_for"):
            cls._registry[cls] = cls.is_datasource_for