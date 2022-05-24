from datetime import datetime

import numpy as np
import pytest

from radiospectra.util import ConditionalDispatch, common_base, get_day, merge, minimal_pairs, to_signed


@pytest.fixture
def oddeven(request):
    f = ConditionalDispatch()
    # Multiply even numbers by two.
    f.add(lambda x: 2 * x, lambda x: x % 2 == 0)
    # Multiply odd numbers by three.
    f.add(lambda x: 3 * x, lambda x: x % 2 == 1)
    return f


def test_dispatch(oddeven):
    assert oddeven(2) == 4
    assert oddeven(3) == 9


def test_wrong_sig(oddeven):
    with pytest.raises(TypeError) as exc_info:
        oddeven(y=2)
    assert "There are no functions matching your input parameter signature." in str(exc_info.value)


def test_nocond():
    f = ConditionalDispatch()
    # Multiply even numbers by two.
    f.add(lambda x: 2 * x, lambda x: x % 2 == 0)
    with pytest.raises(TypeError) as exc_info:
        f(3)
        assert "Your input did not fulfill the condition for any function." in str(exc_info.value)


def test_else():
    f = ConditionalDispatch()
    # Multiply even numbers by two.
    f.add(lambda x: 2 * x, lambda x: x % 2 == 0)
    f.add(lambda x: 3 * x)
    assert f(2) == 4
    assert f(3) == 9


def test_else2():
    # This verifies else branches do not catch cases that are covered
    # by cases added later.
    f = ConditionalDispatch()
    # Because gcd(2, 3) == 1, 2 | x and 3 | x are mutually exclusive.
    f.add(lambda x: 2 * x, lambda x: x % 2 == 0)
    f.add(lambda x: 3 * x)
    f.add(lambda x: 4 * x, lambda x: x % 3 == 0)
    assert f(2) == 4
    assert f(3) == 12
    assert f(5) == 15


def test_types():
    f = ConditionalDispatch()
    f.add(lambda x: 2 * x, lambda x: x % 2 == 0, [int])
    with pytest.raises(TypeError):
        f(2.0)


def test_minimal_pairs():
    """
    This should return the pairs of elements from list1 and list2 with minimal difference between.

    their values.
    """
    list1 = [0, 5, 10, 15, 20, 25]
    list2 = [3, 12, 19, 21, 26, 29]
    assert list(minimal_pairs(list1, list2)) == [(1, 0, 2), (2, 1, 2), (4, 2, 1), (5, 4, 1)]


def test_get_day():
    end_of_day = datetime(year=2017, month=1, day=1, hour=23, minute=59, second=59, microsecond=999)

    begining_of_day = get_day(end_of_day)
    assert begining_of_day.year == 2017
    assert begining_of_day.month == 1
    assert begining_of_day.day == 1
    assert begining_of_day.hour == 0
    assert begining_of_day.minute == 0
    assert begining_of_day.second == 0
    assert begining_of_day.microsecond == 0


def test_common_base():
    """
    This should return the base class common to each object in objs.
    """

    class TestA(object):
        """
        Base test class.
        """

    class TestB(TestA):
        """
        First inherited class.
        """

    class TestC(TestA):
        """
        Second inherited class.
        """

    inst_b = TestB()
    inst_c = TestC()
    objs = [inst_b, inst_c]
    assert common_base(objs) == TestA


def test_merge():
    """
    This should return a sorted (from greatest to least) merged list from list1 and list2.
    """
    list1 = [13, 11, 9, 7, 5, 3, 1]
    list2 = [14, 12, 10, 8, 6, 4, 2]
    result = list(merge([list1, list2]))
    assert result[::-1] == sorted(result)

    assert list(merge([[], [1], []])) == [1]


def test_to_signed():
    """
    This should return a signed type that can hold uint32 and ensure that an exception is raised.

    when attempting to convert an unsigned 64 bit integer to an integer.
    """
    assert to_signed(np.dtype("uint32")) == np.dtype("int64")

    with pytest.raises(ValueError):
        to_signed(np.dtype("uint64")) == np.dtype("int64")
