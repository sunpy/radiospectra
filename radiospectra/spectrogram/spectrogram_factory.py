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
from astropy.time import Time

from sunpy.data import cache
from sunpy.net import attrs as a
from sunpy.sun.constants import sfu
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
        extensions = file.suffixes
        first_extension = extensions[0].lower()
        if first_extension == ".dat":
            return self._read_dat(file)
        elif first_extension in (".r1", ".r2"):
            return [self._read_idl_sav(file, instrument="waves")]
        elif first_extension == ".cdf":
            cdf = self._read_cdf(file)
            if isinstance(cdf, list):
                return cdf
            return [cdf]
        elif first_extension == ".srs":
            return [self._read_srs(file)]
        elif first_extension in (".fits", ".fit", ".fts", "fit.gz"):
            return [self._read_fits(file)]
        else:
            raise ValueError(f"Extension {extensions[0]} not supported.")

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

        if (
            cdf_globals.get("Project", "")[0] == "PSP"
            and cdf_globals.get("Source_name")[0] == "PSP_FLD>Parker Solar Probe FIELDS"
            and "Radio Frequency Spectrometer" in cdf_globals.get("Descriptor")[0]
        ):
            short, _long = cdf_globals["Descriptor"][0].split(">")

            detector = short[4:].lower()
            times, data, freqs = (
                cdf.varget(name)
                for name in [
                    f"epoch_{detector}_auto_averages_ch0_V1V2",
                    f"psp_fld_l2_rfs_{detector}_auto_averages_ch0_V1V2",
                    f"frequency_{detector}_auto_averages_ch0_V1V2",
                ]
            )
            times = Time("J2000.0", scale="tt") + (times << u.ns)
            freqs = freqs[0, :] << u.Hz
            data = data.T << u.Unit("Volt**2/Hz")
            meta = {
                "cdf_globals": cdf_globals,
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
        elif "SOLO" in cdf_globals.get("Project", "")[0]:
            data_type = cdf_globals.get("Data_type", [""])[0]
            data_descriptor = cdf_globals.get("Descriptor", "")[0]
            if "RPW-HFR-SURV" not in data_descriptor and "RPW-TNR-SURV-FLUX" not in data_descriptor:
                raise ValueError(
                    f"Currently radiospectra supports Level 2 HFR survey data "
                    "and Level 3 HFR, TNR survey data the file "
                    f"{file.name} is {cdf_globals.get('Logical_source_description', [''])[0]}"
                )
            if "L3" in data_type:
                epoch = cdf.varget("Epoch")
                times = Time("J2000.0") + epoch * u.ns
                freqs = cdf.varget("FREQUENCY") << u.Unit(cdf.varattsget("FREQUENCY")["UNITS"])
                data = cdf.varget("PSD_SFU")
                data = np.squeeze(data).T << sfu
                detector = cdf_globals.get("Instrument", [""])[0].split(">")[0]
                meta = {
                    "cdf_globals": cdf_globals,
                    "detector": detector,
                    "instrument": "RPW",
                    "observatory": "SOLO",
                    "start_time": times[0],
                    "end_time": times[-1],
                    "wavelength": a.Wavelength(freqs.min(), freqs.max()),
                    "times": times,
                    "freqs": freqs,
                }
                return data, meta
            elif "L2" in data_type:
                # FREQUENCY_BAND_LABELS = ["HF1", "HF2"]
                # SURVEY_MODE_LABELS = ["SURVEY_NORMAL", "SURVEY_BURST"]
                # CHANNEL_LABELS = ["1", "2"]
                SENSOR_MAPPING = {
                    1: "V1",
                    2: "V2",
                    3: "V3",
                    4: "V1-V2",
                    5: "V2-V3",
                    6: "V3-V1",
                    7: "B_MF",
                    9: "HF_V1-V2",
                    10: "HF_V2-V3",
                    11: "HF_V3-V1",
                }

                # Extract variables
                all_times = Time("J2000.0") + cdf.varget("EPOCH") * u.Unit(cdf.varattsget("EPOCH")["UNITS"])
                all_freqs = cdf.varget("FREQUENCY") << u.Unit(cdf.varattsget("FREQUENCY")["UNITS"])

                sweep_start_indices = np.asarray(np.diff(cdf.varget("SWEEP_NUM")) != 0).nonzero()
                sweep_start_indices = np.insert((sweep_start_indices[0] + 1), 0, 0)
                times = all_times[sweep_start_indices]

                sensor = cdf.varget("SENSOR_CONFIG")
                np.unique(cdf.varget("FREQUENCY"))
                band = cdf.varget("HFR_BAND")

                u.Unit(cdf.varattsget("AGC1").get("UNIT", "V^2/Hz"))
                agc1 = cdf.varget("AGC1")
                agc2 = cdf.varget("AGC2")

                # Define number of records
                n_rec = band.shape[0]
                # Get Epoch times of first sample of each sweep in the file
                sweep_times = times
                nt = len(sweep_times)
                # Get complete list of HFR frequency values
                hfr_frequency = 375 + 50 * np.arange(321)  # This is a guess something between 320 and 324
                nf = len(hfr_frequency)

                # Initialize output 2D array containing voltage spectral power values in V^2/Hz
                # Dims = (channels[2], time of the first sweep sample[len(time)], frequency[192])
                specs = np.empty((2, nt, nf))
                # Fill 2D array with NaN for HRF frequencies not actually measured in the file
                specs[:] = np.nan

                # Get list of first index of sweeps
                isweep = sweep_start_indices[:]
                # Get number of sweeps
                n_sweeps = len(isweep)
                # Insert an element in the end of the isweep list
                # containing the end of the latest sweep
                # (required for the loop below, in order to have
                # a start/end index range for each sweep)
                isweep = np.insert(isweep, n_sweeps, n_rec)

                # Initialize sensor_config
                sensor_config = np.zeros((2, nt), dtype=object)
                tm = []
                # Perform a loop on each sweep
                for i in range(n_sweeps):
                    # Get first and last index of the sweep
                    i0 = isweep[i]
                    i1 = isweep[i + 1]

                    ts = all_times[i0]
                    te = all_times[i1 - 1]
                    tt = (te - ts) * 0.5 + ts
                    tm.append(tt)

                    # Get indices of the actual frequency channels in the frequency vector
                    freq_indices = ((all_freqs[i0:i1].value - 375) / 50).astype(int)

                    # fill output 2D array
                    specs[0, i, freq_indices] = agc1[i0:i1]
                    specs[1, i, freq_indices] = agc2[i0:i1]

                    # Fill sensor config
                    sensor_config[0, i] = SENSOR_MAPPING[sensor[i0, 0]]
                    sensor_config[1, i] = SENSOR_MAPPING[sensor[i0, 1]]

                # Define hfr bands
                hfc = np.array(["HF1", "HF2"])
                hfc[band[:100] - 1]

                hfr_frequency = hfr_frequency << u.kHz

                res = []
                if np.any(agc1):
                    meta1 = {
                        "cdf_globals": cdf_globals,
                        "detector": "RPW-AGC1",
                        "instrument": "RPW",
                        "observatory": "SOLO",
                        "start_time": times[0],
                        "end_time": times[-1],
                        "wavelength": a.Wavelength(hfr_frequency.min(), hfr_frequency.max()),
                        "times": times,
                        "freqs": hfr_frequency,
                    }
                    res.append((specs[0].T, meta1))
                if np.any(agc2):
                    meta2 = {
                        "cdf_globals": cdf_globals,
                        "detector": "RPW-AGC2",
                        "instrument": "RPW",
                        "observatory": "SOLO",
                        "start_time": times[0],
                        "end_time": times[-1],
                        "wavelength": a.Wavelength(hfr_frequency.min(), hfr_frequency.max()),
                        "times": times,
                        "freqs": hfr_frequency,
                    }
                    res.append((specs[1].T, meta2))
                return res

    @staticmethod
    def _read_fits(file):
        hd_pairs = fits.open(file)
        if "e-CALLISTO" in hd_pairs[0].header.get("CONTENT", ""):
            return hd_pairs[0].header, hd_pairs
        elif hd_pairs[0].header.get("TELESCOP", "") == "EOVSA":
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
