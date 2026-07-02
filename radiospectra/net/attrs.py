from sunpy.net.attr import SimpleAttr

__all__ = ["Spacecraft", "Observatory", "PolType"]


class Spacecraft(SimpleAttr):  # type: ignore[misc]
    """
    The STEREO Spacecraft A (Ahead) or B (Behind).
    """


class Observatory(SimpleAttr):  # type: ignore[misc]
    """
    Observatory.
    """


class PolType(SimpleAttr):  # type: ignore[misc]
    """
    Polarisation Type.
    """
