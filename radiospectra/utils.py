from ndcube.extra_coords.table_coord import QuantityTableCoordinate, TimeTableCoordinate

import astropy.units as u

__all__ = ["subband_to_freq", "build_spectrogram_wcs"]


def subband_to_freq(subband, obs_mode):
    """
    Converts LOFAR single station subbands to frequency

    Parameters
    ----------
    subband : `int`
        Subband number.
    obs_mode : `int`
        Observation mode 3, 5, 7.

    Return
    ------
    `astropy.units.Quantity`
        Frequency in MHz
    """
    nyq_zone_dict = {3: 1, 5: 2, 7: 3}
    if obs_mode not in nyq_zone_dict:
        raise ValueError(f"Observation mode {obs_mode} not supported, only 3, 5, 7 are supported.")
    nyq_zone = nyq_zone_dict[obs_mode]
    clock_dict = {3: 200, 4: 160, 5: 200, 6: 160, 7: 200}  # MHz
    clock = clock_dict[obs_mode]
    freq = (nyq_zone - 1 + subband / 512) * (clock / 2)
    return freq * u.MHz  # MHz


@u.quantity_input
def build_spectrogram_wcs(time, frequency: u.Hz, reference_time=None):
    """
    Build a generalized world coordinate system (gwcs) from time and frequency arrays.

    Parameters
    ----------
    time: `astropy.time.Time`
    frequency: `astropy.units.Quantity`
    reference_time: `astropy.time.Time`, optional
        Reference time for the time coordinate. Defaults to the first time in the
        time coordinate.
    """
    time_coord = TimeTableCoordinate(time, names="time", physical_types="time", reference_time=reference_time)
    frequency_coord = QuantityTableCoordinate(frequency, names="frequency", physical_types="em.freq")
    return (time_coord & frequency_coord).wcs
