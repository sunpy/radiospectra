from sunpy.net.attr import SimpleAttr

__all__ = ["Spacecraft", "Observatory", "PolType"]


class Spacecraft(SimpleAttr):
    """
    The STEREO Spacecraft A (Ahead) or B (Behind).
    """


class Observatory(SimpleAttr):
    """
    Observatory.
    """


class PolType(SimpleAttr):
    """
    Polarisation Type.
    """
