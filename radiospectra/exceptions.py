__all__ = ["NoSpectrogramInFileError", "SpectraMetaValidationError"]


class NoSpectrogramInFileError(Exception):
    pass


class SpectraMetaValidationError(AttributeError):
    pass
