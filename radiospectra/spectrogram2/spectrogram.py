import os
import glob
import gzip
import struct
import pathlib
import warnings
from pathlib import Path
from collections import OrderedDict
from urllib.request import Request, urlopen

import cdflib
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.image import NonUniformImage
from scipy.io import readsav

import astropy.units as u
from astropy.io import fits
from astropy.io.fits import Header
from astropy.time import Time
from astropy.visualization import quantity_support
from sunpy.data import cache
from sunpy.net import attrs as a
from sunpy.time import parse_time
from sunpy.util.datatype_factory_base import (
    BasicRegistrationFactory,
    MultipleMatchError,
    NoMatchError,
    ValidationFunctionError,
)
from sunpy.util.exceptions import SunpyUserWarning
from sunpy.util.functools import seconddispatch
from sunpy.util.metadata import MetaDict
from sunpy.util.util import expand_list

SUPPORTED_ARRAY_TYPES = (np.ndarray,)
try:
    import dask.array

    SUPPORTED_ARRAY_TYPES += (dask.array.Array,)
except ImportError:
    pass

quantity_support()

__all__ = ["SpectrogramFactory", "Spectrogram", "GenericSpectrogram"]


class NoSpectrogramInFileError(Exception):
    pass


class SpectraMetaValidationError(AttributeError):
    pass


# Can use sunpy.until.io once min version has these
def is_url(arg):
    try:
        urlopen(arg)
    except Exception:
        return False
    return True


# In python<3.8 paths with un-representable chars (ie. '*' on windows)
# raise an error, so make our own version that returns False instead of
# erroring. These can be removed when we support python >= 3.8
# https://docs.python.org/3/library/pathlib.html#methods
def is_file(path):
    try:
        return path.is_file()
    except Exception:
        return False


def is_dir(path):
    try:
        return path.is_dir()
    except Exception:
        return False


def possibly_a_path(obj):
    """
    Check if ``obj`` can be coerced into a pathlib.Path object.

    Does *not* check if the path exists.
    """
    try:
        pathlib.Path(obj)
        return True
    except Exception:
        return False


def parse_path(path, f, **kwargs):
    """
    Read in a series of files at *path* using the function *f*.

    Parameters
    ----------
    path : pathlib.Path
    f : callable
        Must return a list of read-in data.
    kwargs :
        Additional keyword arguments are handed to ``f``.

    Returns
    -------
    list
        List of files read in by ``f``.
    """
    if not isinstance(path, os.PathLike):
        raise ValueError("path must be a pathlib.Path object")
    path = path.expanduser()
    if is_file(path):
        return [f(path, **kwargs)]
    elif is_dir(path):
        read_files = []
        for afile in sorted(path.glob("*")):
            read_files += f(afile, **kwargs)
        return read_files
    elif glob.glob(str(path)):
        read_files = []
        for afile in sorted(glob.glob(str(path))):
            read_files += f(afile, **kwargs)
        return read_files
    else:
        raise ValueError(f"Did not find any files at {path}")


class PcolormeshPlotMixin:
    """
    Class provides plotting functions using `~pcolormesh`.
    """

    def plot(self, axes=None, **kwargs):
        """
        Plot the spectrogram.

        Parameters
        ----------
        axes : `matplotlib.axis.Axes`, optional
            The axes where the plot will be added.
        kwargs :
            Arguments pass to the plot call `pcolormesh`.

        Returns
        -------
        """
        if axes is None:
            fig, axes = plt.subplots()
        else:
            fig = axes.get_figure()

        if hasattr(self.data, "value"):
            data = self.data.value
        else:
            data = self.data

        title = f"{self.observatory}, {self.instrument}"
        if self.instrument != self.detector:
            title = f"{title}, {self.detector}"

        axes.set_title(title)
        axes.plot(self.times.datetime[[0, -1]], self.frequencies[[0, -1]], linestyle="None", marker="None")
        axes.pcolormesh(self.times.datetime, self.frequencies.value, data[:-1, :-1], shading="auto", **kwargs)
        axes.set_xlim(self.times.datetime[0], self.times.datetime[-1])
        locator = mdates.AutoDateLocator(minticks=4, maxticks=8)
        formatter = mdates.ConciseDateFormatter(locator)
        axes.xaxis.set_major_locator(locator)
        axes.xaxis.set_major_formatter(formatter)
        fig.autofmt_xdate()


class NonUniformImagePlotMixin:
    """
    Class provides plotting functions using `NonUniformImage`.
    """

    def plotim(self, fig=None, axes=None, **kwargs):
        if axes is None:
            fig, axes = plt.subplots()

        im = NonUniformImage(axes, interpolation="none", **kwargs)
        im.set_data(mdates.date2num(self.times.datetime), self.frequencies.value, self.data)
        axes.images.append(im)


class GenericSpectrogram(PcolormeshPlotMixin, NonUniformImagePlotMixin):
    """
    Base spectrogram class all new spectrograms will inherit.

    Attributes
    ----------
    meta : `dict-like`
        Meta data for the spectrogram.
    data : `numpy.ndarray`
        The spectrogram data itself a 2D array.
    """

    _registry = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "is_datasource_for"):
            cls._registry[cls] = cls.is_datasource_for

    def __init__(self, data, meta, **kwargs):
        self.data = data
        self.meta = meta

        self._validate_meta()

    @property
    def observatory(self):
        """
        The name of the observatory which recorded the spectrogram.
        """
        return self.meta["observatory"].upper()

    @property
    def instrument(self):
        """
        The name of the instrument which recorded the spectrogram.
        """
        return self.meta["instrument"].upper()

    @property
    def detector(self):
        """
        The detector which recorded the spectrogram.
        """
        return self.meta["detector"].upper()

    @property
    def start_time(self):
        """
        The start time of the spectrogram.
        """
        return self.meta["start_time"]

    @property
    def end_time(self):
        """
        The end time of the spectrogram.
        """
        return self.meta["end_time"]

    @property
    def wavelength(self):
        """
        The wavelength range of the spectrogram.
        """
        return self.meta["wavelength"]

    @property
    def times(self):
        """
        The times of the spectrogram.
        """
        return self.meta["times"]

    @property
    def frequencies(self):
        """
        The frequencies of the spectrogram.
        """
        return self.meta["freqs"]

    def _validate_meta(self):
        """
        Validates the meta-information associated with a Spectrogram.

        This method includes very basic validation checks which apply to
        all of the kinds of files that radiospectra can read.
        Datasource-specific validation should be handled in the relevant
        file in the radiospectra.spectrogram2.sources file.
        """
        msg = "Spectrogram coordinate units for {} axis not present in metadata."
        err_message = []
        for i, ax in enumerate(["times", "freqs"]):
            if self.meta.get(ax) is None:
                err_message.append(msg.format(ax))

        if err_message:
            raise SpectraMetaValidationError("\n".join(err_message))

    def __repr__(self):
        return (
            f"<{self.__class__.__name__} {self.observatory}, {self.instrument}, {self.detector}"
            f" {self.wavelength.min} - {self.wavelength.max},"
            f" {self.start_time.isot} to {self.end_time.isot}>"
        )


class SpectrogramFactory(BasicRegistrationFactory):
    """
    A factory for generating spectrograms.

    Parameters
    ----------
    \\*inputs
        `str` or `pathlib.Path` to the file.

    Returns
    -------
    `radiospectra.spectrogram2.Spectrogram`
        The spectrogram for the give file
    """

    def _validate_meta(self, meta):
        """
        Validate a meta argument.
        """
        if isinstance(meta, Header):
            return True
        elif isinstance(meta, dict):
            return True
        else:
            return False

    def _parse_args(self, *args, silence_errors=False, **kwargs):
        """
        Parses an args list into data-header pairs.

        args can contain any mixture of the following
        entries:

        * tuples of data,header
        * data, header not in a tuple
        * data, wcs object in a tuple
        * data, wcs object not in a tuple
        * filename, as a str or pathlib.Path, which will be read
        * directory, as a str or pathlib.Path, from which all files will be read
        * glob, from which all files will be read
        * url, which will be downloaded and read
        * lists containing any of the above.

        Example
        -------
        self._parse_args(data, header,
                         (data, header),
                         ['file1', 'file2', 'file3'],
                         'file4',
                         'directory1',
                         '*.fits')
        """
        # Account for nested lists of items
        args = expand_list(args)

        # Sanitise the input so that each 'type' of input corresponds to a different
        # class, so single dispatch can be used later
        nargs = len(args)
        i = 0
        while i < nargs:
            arg = args[i]
            if isinstance(arg, SUPPORTED_ARRAY_TYPES):
                # The next two items are data and a header
                data = args.pop(i)
                header = args.pop(i)
                args.insert(i, (data, header))
                nargs -= 1
            elif isinstance(arg, str) and is_url(arg):
                # Replace URL string with a Request object to dispatch on later
                args[i] = Request(arg)
            elif possibly_a_path(arg):
                # Replace path strings with Path objects
                args[i] = pathlib.Path(arg)
            i += 1

        # Parse the arguments
        # Note that this list can also contain GenericSpectrogram if they are directly given to
        # the factory
        data_header_pairs = []
        for arg in args:
            try:
                data_header_pairs += self._parse_arg(arg, **kwargs)
            except NoSpectrogramInFileError as e:
                if not silence_errors:
                    raise
                warnings.warn(f"One of the arguments failed to parse with error: {e}", SunpyUserWarning)

        return data_header_pairs

    # Note that post python 3.8 this can be @functools.singledispatchmethod
    @seconddispatch
    def _parse_arg(self, arg, **kwargs):
        """
        Take a factory input and parse into (data, header) pairs.

        Must return a list, even if only one pair is returned.
        """
        raise ValueError(f"Invalid input: {arg}")

    @_parse_arg.register(tuple)
    def _parse_tuple(self, arg, **kwargs):
        # Data-header
        data, header = arg
        pair = data, header
        if self._validate_meta(header):
            pair = (data, OrderedDict(header))
        return [pair]

    @_parse_arg.register(GenericSpectrogram)
    def _parse_map(self, arg, **kwargs):
        return [arg]

    @_parse_arg.register(Request)
    def _parse_url(self, arg, **kwargs):
        url = arg.full_url
        path = str(cache.download(url).absolute())
        pairs = self._read_file(path, **kwargs)
        return pairs

    @_parse_arg.register(pathlib.Path)
    def _parse_path(self, arg, **kwargs):
        return parse_path(arg, self._read_file, **kwargs)

    def __call__(self, *args, silence_errors=False, **kwargs):
        """
        Method for running the factory.

        Takes arbitrary arguments and keyword arguments and passes
        them to a sequence of pre-registered types to determine which is the correct spectrogram-
        type to build. Arguments args and kwargs are passed through to the validation function and
        to the constructor for the final type. For spectrogram types, validation function must take
        a data-header pair as an argument.

        Parameters
        ----------
        silence_errors : `bool`, optional
            If set, ignore data-header pairs which cause an exception.
            Default is ``False``.

        Notes
        -----
        Extra keyword arguments are passed through to `sunpy.io.read_file` such
        as `memmap` for FITS files.
        """
        data_header_pairs = self._parse_args(*args, silence_errors=silence_errors, **kwargs)
        new_maps = list()

        # Loop over each registered type and check to see if WidgetType
        # matches the arguments.  If it does, use that type.
        for pair in data_header_pairs:
            if isinstance(pair, GenericSpectrogram):
                new_maps.append(pair)
                continue
            data, header = pair
            meta = MetaDict(header)

            try:
                new_map = self._check_registered_widgets(data, meta, **kwargs)
                new_maps.append(new_map)
            except (NoMatchError, MultipleMatchError, ValidationFunctionError, SpectraMetaValidationError) as e:
                if not silence_errors:
                    raise
                warnings.warn(f"One of the data, header pairs failed to validate with: {e}", SunpyUserWarning)

        if not len(new_maps):
            raise RuntimeError("No maps loaded")

        if len(new_maps) == 1:
            return new_maps[0]

        return new_maps

    def _check_registered_widgets(self, data, meta, **kwargs):

        candidate_widget_types = list()

        for key in self.registry:

            # Call the registered validation function for each registered class
            if self.registry[key](data, meta, **kwargs):
                candidate_widget_types.append(key)

        n_matches = len(candidate_widget_types)

        if n_matches == 0:
            if self.default_widget_type is None:
                raise NoMatchError("No types match specified arguments and no default is set.")
            else:
                candidate_widget_types = [self.default_widget_type]
        elif n_matches > 1:
            raise MultipleMatchError(
                "Too many candidate types identified "
                f"({candidate_widget_types}). "
                "Specify enough keywords to guarantee unique type "
                "identification."
            )

        # Only one is found
        WidgetType = candidate_widget_types[0]

        return WidgetType(data, meta, **kwargs)

    def _read_file(self, file, **kwargs):
        file = Path(file)
        extensions = file.suffixes
        first_extension = extensions[0].lower()
        if first_extension == ".dat":
            return self._read_dat(file)
        elif first_extension in (".r1", ".r2"):
            return self._read_idl_sav(file, instrument="waves")
        elif first_extension == ".cdf":
            return self._read_cdf(file)
        elif first_extension == ".srs":
            return self._read_srs(file)
        elif first_extension in (".fits", ".fit", ".fts", "fit.gz"):
            return self._read_fits(file)
        else:
            raise ValueError(f"Extension {extensions[0]} not supported.")

    @staticmethod
    def _read_dat(file):
        if "swaves" in file.name:
            name, prod, date, spacecraft, receiver = file.stem.split("_")
            # frequency range
            freqs = np.genfromtxt(file, max_rows=1) * u.kHz
            # bg which is already subtracted from data
            bg = np.genfromtxt(file, skip_header=1, max_rows=1)
            # data
            data = np.genfromtxt(file, skip_header=2)
            times = data[:, 0] * u.min
            data = data[:, 1:].T

            meta = {
                "instrument": name,
                "observatory": f"STEREO {spacecraft.upper()}",
                "product": prod,
                "start_time": Time.strptime(date, "%Y%m%d"),
                "wavelength": a.Wavelength(freqs[0], freqs[-1]),
                "detector": receiver,
                "freqs": freqs,
                "background": bg,
            }

            meta["times"] = meta["start_time"] + times
            meta["end_time"] = meta["start_time"] + times[-1]
            return data, meta

    @staticmethod
    def _read_srs(file):

        with file.open("rb") as buff:
            data = buff.read()
            if file.suffixes[-1] == ".gz":
                data = gzip.decompress(data)

        # Data is store as a series of records made of different numbers of bytes
        # General header information
        # 1		Year (last 2 digits)				Byte integer (unsigned)
        # 2		Month number (1 to 12)			    "
        # 3		Day (1 to 31)					    "
        # 4		Hour (0 to 23 UT)				    "
        # 5		Minute (0 to 59)				    "
        # 6		Second at start of scan (0 to 59)	"
        # 7		Site Number (0 to 255)			    "
        # 8		Number of bands in the record (2)	"
        #
        # Band 1 (A-band) header information
        # 9,10		Start Frequency (MHz)			    Word integer (16 bits)
        # 11,12		End Frequency (MHz)			        "
        # 13,14		Number of bytes in data record (401)"
        # 15		Analyser reference level		    Byte integer
        # 16		Analyser attenuation (dB)		    "
        #
        # Band 2 (B-band) header information
        # 17-24		As for band 1
        #
        # Spectrum Analyser data
        # 25-425	401 data bytes for band 1 (A-band)
        # 426-826	401 data bytes for band 2 (B-band)
        record_struc = struct.Struct("B" * 8 + "H" * 3 + "B" * 2 + "H" * 3 + "B" * 2 + "B" * 401 + "B" * 401)

        records = record_struc.iter_unpack(data)

        # Map of numeric records to locations
        site_map = {1: "Palehua", 2: "Holloman", 3: "Learmonth", 4: "San Vito"}

        df = pd.DataFrame([(*r[:18], np.array(r[18:419]), np.array(r[419:820])) for r in records])
        df.columns = [
            "year",
            "month",
            "day",
            "hour",
            "minute",
            "second",
            "site",
            " num_bands",
            "start_freq1",
            "end_freq1",
            "num_bytes1",
            "analyser_ref1",
            "analyser_atten1",
            "start_freq2",
            "end_freq2",
            "num_bytes2",
            "analyser_ref2",
            "analyser_atten2",
            "spec1",
            "spec2",
        ]

        # Hack to make to_datetime work - earliest dates seem to be 2000 and won't be
        # around in 3000!
        df["year"] = df["year"] + 2000
        df["time"] = pd.to_datetime(df[["year", "month", "day", "hour", "minute", "second"]])

        # Equations taken from document
        n = np.arange(1, 402)
        freq_a = (25 + 50 * (n - 1) / 400) * u.MHz
        freq_b = (75 + 105 * (n - 1) / 400) * u.MHz
        freqs = np.hstack([freq_a, freq_b])

        data = np.hstack([np.vstack(df[name].to_numpy()) for name in ["spec1", "spec2"]]).T
        times = Time(df["time"])

        meta = {
            "instrument": "RSTN",
            "observatory": site_map[df["site"][0]],
            "start_time": times[0],
            "end_time": times[-1],
            "detector": "RSTN",
            "wavelength": a.Wavelength(freqs[0], freqs[-1]),
            "freqs": freqs,
            "times": times,
        }

        return data, meta

    @staticmethod
    def _read_cdf(file):
        cdf = cdflib.CDF(file)
        cdf_meta = cdf.globalattsget()
        if (
            cdf_meta.get("Project", "") == "PSP"
            and cdf_meta.get("Source_name") == "PSP_FLD>Parker Solar Probe FIELDS"
            and "Radio Frequency Spectrometer" in cdf_meta.get("Descriptor")
        ):
            short, _long = cdf_meta["Descriptor"].split(">")
            detector = short[4:].lower()

            times, data, freqs = [
                cdf.varget(name)
                for name in [
                    f"epoch_{detector}_auto_averages_ch0_V1V2",
                    f"psp_fld_l2_rfs_{detector}_auto_averages_ch0_V1V2",
                    f"frequency_{detector}_auto_averages_ch0_V1V2",
                ]
            ]

            times = Time(times << u.ns, format="cdf_tt2000")
            freqs = freqs[0, :] << u.Hz
            data = data.T << u.Unit("Volt**2/Hz")

            meta = {
                "cdf_meta": cdf_meta,
                "detector": detector,
                "instrument": "FIELDS/RFS",
                "observatory": "PSP",
                "start_time": times[0],
                "end_time": times[-1],
                "wavelength": a.Wavelength(freqs.min(), freqs.max()),
                "times": times,
                "freqs": freqs,
            }
            return data, meta

    @staticmethod
    def _read_fits(file):
        hd_pairs = fits.open(file)

        if "e-CALLISTO" in hd_pairs[0].header.get("CONTENT", ""):
            data = hd_pairs[0].data
            times = hd_pairs[1].data["TIME"].flatten() * u.s
            freqs = hd_pairs[1].data["FREQUENCY"].flatten() * u.MHz
            start_time = parse_time(hd_pairs[0].header["DATE-OBS"] + " " + hd_pairs[0].header["TIME-OBS"])
            end_time = parse_time(hd_pairs[0].header["DATE-END"] + " " + hd_pairs[0].header["TIME-END"])
            times = start_time + times
            meta = {
                "fits_meta": hd_pairs[0].header,
                "detector": "e-CALLISTO",
                "instrument": "e-CALLISTO",
                "observatory": hd_pairs[0].header["INSTRUME"],
                "start_time": start_time,
                "end_time": end_time,
                "wavelength": a.Wavelength(freqs.min(), freqs.max()),
                "times": times,
                "freqs": freqs,
            }
            return data, meta
        elif hd_pairs[0].header.get("TELESCOP", "") == "EOVSA":
            times = Time(hd_pairs[2].data["mjd"] + hd_pairs[2].data["time"] / 1000.0 / 86400.0, format="mjd")
            freqs = hd_pairs[1].data["sfreq"] * u.GHz
            data = hd_pairs[0].data
            start_time = parse_time(hd_pairs[0].header["DATE_OBS"])
            end_time = parse_time(hd_pairs[0].header["DATE_END"])

            meta = {
                "fits_meta": hd_pairs[0].header,
                "detector": "EOVSA",
                "instrument": "EOVSA",
                "observatory": "Owens Valley",
                "start_time": start_time,
                "end_time": end_time,
                "wavelength": a.Wavelength(freqs.min(), freqs.max()),
                "times": times,
                "freqs": freqs,
            }
            return data, meta

    @staticmethod
    def _read_idl_sav(file, instrument=None):
        data = readsav(file)
        if instrument == "waves":
            # See https://solar-radio.gsfc.nasa.gov/wind/one_minute_doc.html
            data_array = data["arrayb"]
            # frequency range
            if file.suffix == ".R1":
                freqs = np.linspace(20, 1040, 256) * u.kHz
                receiver = "RAD1"
            elif file.suffix == ".R2":
                freqs = np.linspace(1.075, 13.825, 256) * u.MHz
                receiver = "RAD2"
            # bg which is already subtracted from data ?
            bg = data_array[:, -1]
            data = data_array[:, :-1]

            start_time = Time.strptime(file.stem, "%Y%m%d")
            end_time = start_time + 86399 * u.s
            times = start_time + (np.arange(1440) * 60 + 30) * u.s

            meta = {
                "instrument": "WAVES",
                "observatory": "WIND",
                "start_time": start_time,
                "end_time": end_time,
                "wavelength": a.Wavelength(freqs[0], freqs[-1]),
                "detector": receiver,
                "freqs": freqs,
                "times": times,
                "background": bg,
            }

            return data, meta


Spectrogram = SpectrogramFactory(registry=GenericSpectrogram._registry, default_widget_type=GenericSpectrogram)
