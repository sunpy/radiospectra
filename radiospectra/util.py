"""
Offer a callable object that dispatches based on arbitrary conditions and function signature.

That
means, whenever it is called, it finds the registered methods that match the input's signature and
then checks for user-defined conditions and types.

First, we need to create a new ConditionalDispatch

>>> from radiospectra.util import ConditionalDispatch
>>> fun = ConditionalDispatch()

We then can start adding branches, in this case we add a branch for
even integers, in which case the function applied is a multiplication by
three.

>>> fun.add(lambda x: 3 * x, lambda x: x % 2 == 0, [int])

By adding the other branch (odd), the function can be used for all integers.
In the case of an odd integer, we double the input. Please note that the system
has no way of verifying the conditions are mutually exclusive. In some cases
it can even be useful to use not mutually exclusive conditions, in which case
the branch that was added the earliest is executed.

>>> fun.add(lambda x: 2 * x, lambda x: x % 2 == 1, [int])

We can verify this is working.

>>> fun(2)
6
>>> fun(3)
6

And that using a float, e.g., does not.

>>> fun(3.2)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/florian/Projects/sunpy/sunpy/util/cond_dispatch.py", line 128, in __call__
    "There are no functions matching your input parameter "
TypeError: There are no functions matching your input parameter signature.

We can then add a branch for floats, giving the condition None that means
that this branch is always executed for floats.

>>> fun.add(lambda y: 5 * y, None, [float])

Also note that the float branch takes y, while the integer branch takes x.
Thus, if the user explicitly passes fun(x=1) using a keyword argument, only
the integer branch is considered. This can be useful if the user wants
control over which kind of data they are passing the the function.

>>> fun(2.0)
10.0
>>> fun(y=2)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/florian/Projects/sunpy/sunpy/util/cond_dispatch.py", line 128, in __call__
    "There are no functions matching your input parameter "
TypeError: There are no functions matching your input parameter signature.
>>> fun(y=2.5)
12.5
>>> fun(x=2)
6
>>> fun(x=2.5)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/florian/Projects/sunpy/sunpy/util/cond_dispatch.py", line 128, in __call__
    "There are no functions matching your input parameter "
TypeError: There are no functions matching your input parameter signature.
"""


import os
import glob
import inspect
from datetime import datetime
from itertools import chain, repeat

import numpy as np

from sunpy.util.config import get_and_create_download_dir
from sunpy.util.net import download_file

__all__ = [
    "run_cls",
    "matches_types",
    "arginize",
    "correct_argspec",
    "matches_signature",
    "ConditionalDispatch",
    "fmt_argspec_types",
    "minimal_pairs",
    "get_day",
    "to_signed",
    "common_base",
    "merge",
    "Parent",
]


def merge(items, key=(lambda x: x)):
    """
    Given sorted lists of iterables, return new iterable that returns elements of all iterables.

    sorted with respect to key.
    """
    state = {}
    for item in map(iter, items):
        try:
            first = next(item)
        except StopIteration:
            continue
        else:
            state[item] = (first, key(first))

    while state:
        for item, (value, tk) in list(state.items()):
            # Value is biggest.
            if all(tk >= k for it, (v, k) in list(state.items()) if it is not item):
                yield value
                break
        try:
            n = next(item)
            state[item] = (n, key(n))
        except StopIteration:
            del state[item]


def common_base(objs):
    """
    Find class that every item of objs is an instance of.
    """
    for cls in objs[0].__class__.__mro__:
        if all(isinstance(obj, cls) for obj in objs):
            break
    return cls


def to_signed(dtype):
    """
    Return dtype that can hold data of passed dtype but is signed.

    Raise ValueError if no such dtype
    exists.

    Parameters
    ----------
    dtype : `numpy.dtype`
        dtype whose values the new dtype needs to be able to represent.

    Returns
    -------
    `numpy.dtype`
    """
    if dtype.kind == "u":
        if dtype.itemsize == 8:
            raise ValueError("Cannot losslessly convert uint64 to int.")
        dtype = "int{:d}".format(min(dtype.itemsize * 2 * 8, 64))
    return np.dtype(dtype)


def get_day(dt):
    """
    Return datetime for the beginning of the day of given datetime.
    """
    return datetime(dt.year, dt.month, dt.day)


def minimal_pairs(one, other):
    """
    Find pairs of values in one and other with minimal distance.

    Assumes one and other are sorted in
    the same sort sequence.

    Parameters
    ----------
    one, other : sequence
        Sequence of scalars to find pairs from.

    Returns
    -------
    `tuple`
         Pairs of values in `one` and `other` with minimal distance
    """
    lbestdiff = bestdiff = bestj = besti = None
    for i, freq in enumerate(one):
        lbestj = bestj

        bestdiff, bestj = None, None
        for j, o_freq in enumerate(other[lbestj:]):
            j = lbestj + j if lbestj else j
            diff = abs(freq - o_freq)
            if bestj is not None and diff > bestdiff:
                break

            if bestj is None or bestdiff > diff:
                bestj = j
                bestdiff = diff

        if lbestj is not None and lbestj != bestj:
            yield (besti, lbestj, lbestdiff)
            besti = i
            lbestdiff = bestdiff
        elif lbestdiff is None or bestdiff < lbestdiff:
            besti = i
            lbestdiff = bestdiff

    yield (besti, bestj, lbestdiff)


def run_cls(name):
    """
    Run_cls("foo")(cls, \\*args, \\**kwargs) -> cls.foo(\\*args, \\**kwargs).
    """
    fun = lambda cls, *args, **kwargs: getattr(cls, name)(*args, **kwargs)  # NOQA
    fun.__name__ = str(name)
    fun.run_cls = True
    return fun


def matches_types(fun, types, args, kwargs):
    """
    See if args and kwargs match are instances of types.

    types are given in the order they are defined in the function.
    kwargs are automatically converted into that order.
    """
    return all(isinstance(obj, cls) for obj, cls in list(zip(arginize(fun, args, kwargs), types)))


def arginize(fun, a, kw):
    """
    Turn args and kwargs into args by considering the function signature.
    """
    args, varargs, keywords, defaults = correct_argspec(fun)

    if varargs is not None:
        raise ValueError
    names = args[len(a) :]
    if defaults:
        defs = dict(list(zip(args[-len(defaults) :], defaults)))
    else:
        defs = {}
    return list(a) + [kw.get(name, defs.get(name, None)) for name in names]


def correct_argspec(fun):
    """
    Remove first argument if method is bound.
    """
    fullargspec = inspect.getfullargspec(fun)
    args, varargs, keywords, defaults = fullargspec[0], fullargspec[1], fullargspec[2], fullargspec[3]
    if inspect.ismethod(fun):
        args = args[1:]
    return args, varargs, keywords, defaults


def matches_signature(fun, a, kw):
    """
    Check whether function can be called with a as args and kw as kwargs.
    """
    args, varargs, keywords, defaults = correct_argspec(fun)

    if varargs is None and len(a) > len(args):
        return False
    skw = set(kw)
    sargs = set(args[len(a) :])

    # There mayn't be unexpected parameters unless there is a **kwargs
    # in fun's signature.
    if keywords is None and skw - sargs != set():
        return False
    rest = set(args[len(a) :]) - set(kw)

    # If there are any arguments that weren't passed but do not have
    # defaults, the signature does not match.
    defs = set() if defaults is None else set(defaults)
    if keywords is None and rest > defs:
        return False
    return True


class ConditionalDispatch(object):
    def __init__(self):
        self.funcs = []
        self.nones = []

    @classmethod
    def from_existing(cls, cond_dispatch):
        new = cls()
        new.funcs = cond_dispatch.funcs[:]
        new.nones = cond_dispatch.nones[:]
        return new

    def add_dec(self, condition):
        def _dec(fun):
            self.add(fun, condition)
            return fun

        return _dec

    def add(self, fun, condition=None, types=None, check=True):
        """
        Add fun to ConditionalDispatch under the condition that the arguments must match.

        If condition is left out, the function is executed for every
        input that matches the signature. Functions are considered in
        the order they are added, but ones with condition=None are
        considered as the last: that means, a function with condition
        None serves as an else branch for that signature. conditions
        must be mutually exclusive because otherwise which will be
        executed depends on the order they are added in. Function
        signatures of fun and condition must match (if fun is bound, the
        bound parameter needs to be left out in condition).
        """
        if condition is None:
            self.nones.append((fun, types))
        elif check and correct_argspec(fun) != correct_argspec(condition):
            raise ValueError("Signature of condition must match signature of fun.")
        else:
            self.funcs.append((fun, condition, types))

    def __call__(self, *args, **kwargs):
        matched = False
        for fun, condition, types in self.funcs:
            if matches_signature(condition, args, kwargs) and (
                types is None or matches_types(condition, types, args, kwargs)
            ):
                matched = True
                if condition(*args, **kwargs):
                    return fun(*args, **kwargs)
        for fun, types in self.nones:
            if matches_signature(fun, args, kwargs) and (types is None or matches_types(fun, types, args, kwargs)):
                return fun(*args, **kwargs)

        if matched:
            raise TypeError("Your input did not fulfill the condition for any function.")
        else:
            raise TypeError("There are no functions matching your input parameter " "signature.")

    def wrapper(self):
        return lambda *args, **kwargs: self(*args, **kwargs)

    def get_signatures(self, prefix="", start=0):
        """
        Return an iterator containing all possible function signatures.

        If prefix is given, use it
        as function name in signatures, else leave it out. If start is given, leave out first n
        elements.

        If start is -1, leave out first element if the function was
        created by run_cls.
        """
        for fun, condition, types in self.funcs:
            if start == -1:
                st = getattr(fun, "run_cls", 0)
            else:
                st = start

            if types is not None:
                yield prefix + fmt_argspec_types(condition, types, st)
            else:
                args, varargs, keywords, defaults = correct_argspec(condition)
                args = args[st:]
                sig_str = str(inspect.signature(fun))
                if sig_str == "(cls, *args, **kwargs)":
                    sig_str = "(cls, \\*args, \\**kwargs)"
                yield prefix + sig_str

        for fun, types in self.nones:
            if types is not None:
                yield prefix + fmt_argspec_types(fun, types, st)
            else:
                args, varargs, keywords = correct_argspec(condition)
                args = args[st:]
                if sig_str == "(cls, *args, **kwargs)":
                    sig_str = "(cls, \\*args, \\**kwargs)"
                yield prefix + sig_str

    def generate_docs(self):
        fns = (item[0] for item in chain(self.funcs, self.nones))
        return "\n\n    ".join(
            "{} -> :meth:`{}`".format(sig, fun.__name__)
            for sig, fun in
            # The 1 prevents the cls from incorrectly being shown in the
            # documentation.
            list(zip(self.get_signatures("create", -1), fns))
        )


def fmt_argspec_types(fun, types, start=0):
    args, varargs, keywords, defaults = correct_argspec(fun)
    args = args[start:]
    types = types[start:]

    NULL = object()
    if defaults is None:
        defaults = []
    defs = chain(repeat(NULL, len(args) - len(defaults)), defaults)

    spec = []
    for key, value, type_ in zip(args, defs, types):
        # This is a work around for a bug introduced during Python 3 porting.
        # for some reason the type was being passed in as a length 1 tuple.
        # This extracts the type under that condition. SM 6/10/15
        if isinstance(type_, tuple) and len(type_) == 1:
            type_ = type_[0]
        if value is NULL:
            spec.append("{}: {}".format(key, type_.__name__))
        else:
            spec.append("{}: {} = {}".format(key, type_.__name__, value))
    if varargs is not None:
        spec.append("*{!s}".format(varargs))
    if keywords is not None:
        spec.append("**{!s}".format(keywords))
    return "(" + ", ".join(spec) + ")"


class Parent(object):
    _create = ConditionalDispatch()

    @classmethod
    def read(cls, filename):
        raise NotImplementedError

    @classmethod
    def read_many(cls, filenames):
        return list(map(cls.read, filenames))

    @classmethod
    def from_glob(cls, pattern):
        """
        Read out files using glob (e.g., ~/BIR_2011*) pattern.

        Returns list of objects made from all matched files.
        """
        return cls.read_many(glob.glob(pattern))

    @classmethod
    def from_single_glob(cls, singlepattern):
        """
        Read out a single file using glob (e.g., ~/BIR_2011*) pattern.

        If more than one file matches the pattern, raise ValueError.
        """
        matches = glob.glob(os.path.expanduser(singlepattern))
        if len(matches) != 1:
            raise ValueError("Invalid number of matches: {:d}".format(len(matches)))
        return cls.read(matches[0])

    @classmethod
    def from_files(cls, filenames):
        """
        Return list of object read from given list of filenames.
        """
        filenames = list(map(os.path.expanduser, filenames))
        return cls.read_many(filenames)

    @classmethod
    def from_file(cls, filename):
        """
        Return object from file.
        """
        filename = os.path.expanduser(filename)
        return cls.read(filename)

    @classmethod
    def from_dir(cls, directory):
        """
        Return list that contains all files in the directory read in.
        """
        directory = os.path.expanduser(directory)
        return cls.read_many(os.path.join(directory, elem) for elem in os.listdir(directory))

    @classmethod
    def from_url(cls, url):
        """
        Return object read from URL.

        Parameters
        ----------
        url : str
            URL to retrieve the data from
        """
        path = download_file(url, get_and_create_download_dir())
        return cls.read(path)


Parent._create.add(
    run_cls("from_file"), lambda cls, filename: os.path.isfile(os.path.expanduser(filename)), [type, str], check=False
)
Parent._create.add(
    # pylint: disable=W0108
    # The lambda is necessary because introspection is performed on the
    # argspec of the function.
    run_cls("from_dir"),
    lambda cls, directory: os.path.isdir(os.path.expanduser(directory)),
    [type, str],
    check=False,
)
# If it is not a kwarg and only one matches, do not return a list.
Parent._create.add(
    run_cls("from_single_glob"),
    lambda cls, singlepattern: ("*" in singlepattern and len(glob.glob(os.path.expanduser(singlepattern))) == 1),
    [type, str],
    check=False,
)
# This case only gets executed under the condition that the previous one wasn't.
# This is either because more than one file matched, or because the user
# explicitly used pattern=, in both cases we want a list.
Parent._create.add(
    run_cls("from_glob"),
    lambda cls, pattern: "*" in pattern and glob.glob(os.path.expanduser(pattern)),
    [type, str],
    check=False,
)
Parent._create.add(run_cls("from_files"), lambda cls, filenames: True, types=[type, list], check=False)
Parent._create.add(run_cls("from_url"), lambda cls, url: True, types=[type, str], check=False)
