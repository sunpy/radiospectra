import os
import datetime

import numpy as np

from radiospectra.spectrogram import REFERENCE, LinearTimeSpectrogram
from radiospectra.util import ConditionalDispatch, get_day

__all__ = ["SWavesSpectrogram"]


class SWavesSpectrogram(LinearTimeSpectrogram):
    _create = ConditionalDispatch.from_existing(LinearTimeSpectrogram._create)
    create = classmethod(_create.wrapper())
    COPY_PROPERTIES = LinearTimeSpectrogram.COPY_PROPERTIES + [("bg", REFERENCE)]

    @staticmethod
    def swavesfile_to_date(filename):
        _, name = os.path.split(filename)
        date = name.split("_")[2]
        return datetime.datetime(int(date[0:4]), int(date[4:6]), int(date[6:]))

    @classmethod
    def read(cls, filename, **kwargs):
        """
        Read in FITS file and return a new SWavesSpectrogram.
        """
        data = np.genfromtxt(filename, skip_header=2)
        time_axis = data[:, 0] * 60.0
        data = data[:, 1:].transpose()
        header = np.genfromtxt(filename, skip_footer=time_axis.size)
        freq_axis = header[0, :]
        bg = header[1, :]
        start = cls.swavesfile_to_date(filename)
        end = start + datetime.timedelta(seconds=time_axis[-1])
        t_delt = 60.0
        t_init = (start - get_day(start)).seconds
        content = ""
        t_label = "Time [UT]"
        f_label = "Frequency [KHz]"

        freq_axis = freq_axis[::-1]
        data = data[::-1, :]

        return cls(data, time_axis, freq_axis, start, end, t_init, t_delt, t_label, f_label, content, bg)

    def __init__(self, data, time_axis, freq_axis, start, end, t_init, t_delt, t_label, f_label, content, bg):
        # Because of how object creation works, there is no avoiding
        # unused arguments in this case.
        # pylint: disable=W0613

        super(SWavesSpectrogram, self).__init__(
            data, time_axis, freq_axis, start, end, t_init, t_delt, t_label, f_label, content, {"SWAVES"}
        )
        self.bg = bg


try:
    SWavesSpectrogram.create.__func__.__doc__ = (
        """ Create SWavesSpectrogram from given input dispatching to the
        appropriate from_* function.

    Possible signatures:

    """
        + SWavesSpectrogram._create.generate_docs()
    )
except AttributeError:
    SWavesSpectrogram.create.__func__.__doc__ = (
        """ Create SWavesSpectrogram from given input dispatching to the
        appropriate from_* function.

    Possible signatures:

    """
        + SWavesSpectrogram._create.generate_docs()
    )
