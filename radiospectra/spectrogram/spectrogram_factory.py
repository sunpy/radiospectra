import pathlib
import warnings
import functools
from pathlib import Path
from collections import OrderedDict
from urllib.request import Request

import cdflib
import numpy as np
from scipy.io import readsav

import astropy.units as u
from astropy.io import fits
from astropy.io.fits import Header

from sunpy.data import cache
from sunpy.net import attrs as a
from sunpy.time import parse_time
from sunpy.util.datatype_factory_base import (
    BasicRegistrationFactory,
    MultipleMatchError,
    NoMatchError,
    ValidationFunctionError,
)
from sunpy.util.exceptions import SunpyUserWarning, warn_user
from sunpy.util.io import is_url, parse_path, possibly_a_path
from sunpy.util.util import expand_list

from radiospectra.exceptions import NoSpectrogramInFileError, SpectraMetaValidationError
from radiospectra.spectrogram.spectrogrambase import GenericSpectrogram

SUPPORTED_ARRAY_TYPES = (np.ndarray,)
try:
    import dask.array

    SUPPORTED_ARRAY_TYPES += (dask.array.Array,)
except ImportError:
    pass

__all__ = ["SpectrogramFactory", "Spectrogram"]


class SpectrogramFactory(BasicRegistrationFactory):
    """
    A factory for generating spectrograms.

    Parameters
    ----------
    \\*inputs
        `str` or `pathlib.Path` to the file.

    Returns
    -------
    `radiospectra.spectrogram.Spectrogram`
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
        # Sanitize the input so that each 'type' of input corresponds to a different
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
        # Note that this list can also contain GenericMaps if they are directly given to the factory
        data_header_pairs = []
        for arg in args:
            try:
                data_header_pairs += self._parse_arg(arg, **kwargs)
            except NoSpectrogramInFileError as e:
                if not silence_errors:
                    raise
                warn_user(f"One of the arguments failed to parse with error: {e}")
        return data_header_pairs

    @functools.singledispatchmethod
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
        for pair in data_header_pairs:
            if isinstance(pair, GenericSpectrogram):
                new_maps.append(pair)
                continue
            # Detect whether the pair is (header, raw_object) or (data, meta).
            # If the first element is a dict or FITS Header, it's a raw pair.
            first = pair[0]
            is_raw = isinstance(first, (dict, Header))
            try:
                new_map = self._check_registered_widgets(pair[0], pair[1], from_raw=is_raw, **kwargs)
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

    def _check_registered_widgets(self, data_or_header, meta_or_raw, from_raw=False, **kwargs):
        candidate_widget_types = list()
        for key in self.registry:
            try:
                if self.registry[key](data_or_header, meta_or_raw, **kwargs):
                    candidate_widget_types.append(key)
            except (KeyError, TypeError, IndexError, AttributeError):
                # Validation function crashed — this widget doesn't match
                continue

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

        WidgetType = candidate_widget_types[0]
        if from_raw:
            return WidgetType.from_raw(data_or_header, meta_or_raw)
        return WidgetType(data_or_header, meta_or_raw, **kwargs)

    def _read_file(self, file, **kwargs):
        file = Path(file)
        extensions = [ext.lower() for ext in file.suffixes]
        if ".dat" in extensions:
            return self._read_dat(file)
        elif ".r1" in extensions or ".r2" in extensions:
            return [self._read_idl_sav(file, instrument="waves")]
        elif ".cdf" in extensions:
            cdf = self._read_cdf(file)
            if isinstance(cdf, list):
                return cdf
            return [cdf]
        elif ".srs" in extensions:
            return [self._read_srs(file)]
        elif any(ext in (".fits", ".fit", ".fts") for ext in extensions):
            fits_res = self._read_fits(file)
            if isinstance(fits_res, list):
                return fits_res
            return [fits_res]
        else:
            raise ValueError(f"Extension {file.suffixes} not supported.")

    @staticmethod
    def _read_dat(file):
        if "swaves" in file.name:
            header = {"file_type": "dat", "instrument": "swaves", "file_path": file}
            return [(header, None)]
        elif "bst" in file.name:
            header = {"file_type": "dat", "instrument": "ILOFAR", "file_path": file}
            return [(header, None)]
        else:
            raise ValueError(f"File {file} not supported.")

    @staticmethod
    def _read_srs(file):
        header = {"file_type": "srs", "instrument": "RSTN", "file_path": file}
        return header, None

    @staticmethod
    def _read_cdf(file):
        cdf = cdflib.CDF(file)
        cdf_globals = cdf.globalattsget()
        header = {"file_type": "cdf", "file_path": file, "cdf_globals": cdf_globals}
        return header, cdf

    @staticmethod
    def _read_fits(file):
        hd_pairs = fits.open(file)
        if "e-CALLISTO" in hd_pairs[0].header.get("CONTENT", ""):
            return hd_pairs[0].header, hd_pairs
        elif hd_pairs[0].header.get("TELESCOP", "") == "EOVSA":
            return hd_pairs[0].header, hd_pairs
        elif hd_pairs[0].header.get("TELESCOP", "") == "NDA":
            return hd_pairs[0].header, hd_pairs
        # Semi standard - spec in primary and time and freq in 1st extension
        try:
            data = hd_pairs[0].data
            times = hd_pairs[1].data["TIME"].flatten() * u.s
            freqs = hd_pairs[1].data["FREQUENCY"].flatten() * u.MHz
            start_time = parse_time(hd_pairs[0].header["DATE-OBS"] + " " + hd_pairs[0].header["TIME-OBS"])
            end_time = parse_time(hd_pairs[0].header["DATE-END"] + " " + hd_pairs[0].header["TIME-END"])
            times = start_time + times
            meta = {
                "fits_meta": hd_pairs[0].header,
                "start_time": start_time,
                "end_time": end_time,
                "wavelength": a.Wavelength(freqs.min(), freqs.max()),
                "times": times,
                "freqs": freqs,
                "instrument": hd_pairs[0].header.get("INSTRUME", ""),
                "observatory": hd_pairs[0].header.get("INSTRUME", ""),
                "detector": hd_pairs[0].header.get("DETECTOR", ""),
            }
            if "e-CALLISTO" in hd_pairs[0].header["CONTENT"]:
                meta["detector"] = "e-CALLISTO"
                meta["instrument"] = "e-CALLISTO"
            return data, meta
        except Exception as e:
            raise ValueError(f"Could not load fits file: {file} into Spectrogram.") from e

    @staticmethod
    def _read_idl_sav(file, instrument=None):
        data = readsav(file)
        # Return (header, raw_object) — parsing moved to WAVESSpectrogram.from_raw
        header = {"file_type": "idl_sav", "instrument": instrument, "file_path": file}
        return header, data


Spectrogram = SpectrogramFactory(registry=GenericSpectrogram._registry, default_widget_type=GenericSpectrogram)
