import pytest

import humanize
from humanize import filesize
from humanize.filesize import naturalsize, suffixes


def test_suffixes_structure():
    assert set(suffixes) == {"decimal", "binary", "gnu"}
    assert len(suffixes["decimal"]) == 10
    assert len(suffixes["binary"]) == 10
    assert len(suffixes["gnu"]) == 10
    assert suffixes["decimal"][0] == "kB"
    assert suffixes["decimal"][-1] == "QB"
    assert suffixes["binary"][0] == "KiB"
    assert suffixes["binary"][-1] == "QiB"
    assert suffixes["gnu"] == "KMGTPEZYRQ"


def test_naturalsize_exported_from_package():
    assert humanize.naturalsize is naturalsize


@pytest.mark.parametrize(
    "value, expected",
    [
        (0, "0 Bytes"),
        (1, "1 Byte"),
        (-1, "-1 Byte"),
        (1.0, "1 Byte"),
        (-1.0, "-1 Byte"),
        (2, "2 Bytes"),
        (300, "300 Bytes"),
        (999, "999 Bytes"),
        (-999, "-999 Bytes"),
        (1.5, "1 Bytes"),
        (-1.5, "-1 Bytes"),
        (999.9, "999 Bytes"),
        (0.0, "0 Bytes"),
    ],
)
def test_naturalsize_small_values_default(value, expected):
    assert naturalsize(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (0, "0 Bytes"),
        (1, "1 Byte"),
        (1023, "1023 Bytes"),
        (-1023, "-1023 Bytes"),
    ],
)
def test_naturalsize_small_values_binary(value, expected):
    assert naturalsize(value, binary=True) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (0, "0B"),
        (1, "1B"),
        (-1, "-1B"),
        (300, "300B"),
        (1000, "1000B"),
        (1023, "1023B"),
        (-300, "-300B"),
        (1.9, "1B"),
    ],
)
def test_naturalsize_small_values_gnu(value, expected):
    assert naturalsize(value, gnu=True) == expected


def test_naturalsize_docstring_examples():
    assert naturalsize(3000000) == "3.0 MB"
    assert naturalsize(300, False, True) == "300B"
    assert naturalsize(3000, False, True) == "2.9K"
    assert naturalsize(3000, False, True, "%.3f") == "2.930K"
    assert naturalsize(3000, True) == "2.9 KiB"
    assert naturalsize(10**28) == "10.0 RB"
    assert naturalsize(10**34 * 3) == "30000.0 QB"
    assert naturalsize(-4096, True) == "-4.0 KiB"


def test_naturalsize_decimal_boundaries():
    assert naturalsize(1000) == "1.0 kB"
    assert naturalsize(1500) == "1.5 kB"
    assert naturalsize(-1500) == "-1.5 kB"
    assert naturalsize(3000) == "3.0 kB"
    assert naturalsize(3000.5) == "3.0 kB"


def test_naturalsize_binary_boundaries():
    assert naturalsize(1024, binary=True) == "1.0 KiB"
    assert naturalsize(1536, binary=True) == "1.5 KiB"
    assert naturalsize(3 * 1024**2, binary=True) == "3.0 MiB"


def test_naturalsize_gnu_boundaries():
    assert naturalsize(1024, gnu=True) == "1.0K"
    assert naturalsize(1536, gnu=True) == "1.5K"
    assert naturalsize(3 * 1024**2, gnu=True) == "3.0M"
    assert naturalsize(-1536, gnu=True) == "-1.5K"


@pytest.mark.parametrize("n", range(1, 11))
def test_naturalsize_every_decimal_suffix(n):
    assert naturalsize(3 * 1000**n) == f"3.0 {suffixes['decimal'][n - 1]}"
    assert naturalsize(-3 * 1000**n) == f"-3.0 {suffixes['decimal'][n - 1]}"


@pytest.mark.parametrize("n", range(1, 11))
def test_naturalsize_every_binary_suffix(n):
    assert (
        naturalsize(3 * 1024**n, binary=True)
        == f"3.0 {suffixes['binary'][n - 1]}"
    )
    assert (
        naturalsize(-3 * 1024**n, binary=True)
        == f"-3.0 {suffixes['binary'][n - 1]}"
    )


@pytest.mark.parametrize("n", range(1, 11))
def test_naturalsize_every_gnu_suffix(n):
    assert naturalsize(3 * 1024**n, gnu=True) == f"3.0{suffixes['gnu'][n - 1]}"
    assert naturalsize(-3 * 1024**n, gnu=True) == f"-3.0{suffixes['gnu'][n - 1]}"


def test_naturalsize_largest_suffix_is_capped():
    assert naturalsize(3 * 1000**11) == "3000.0 QB"
    assert naturalsize(3 * 1000**12) == "3000000.0 QB"
    assert naturalsize(3 * 1024**11, binary=True) == "3072.0 QiB"
    assert naturalsize(3 * 1024**11, gnu=True) == "3072.0Q"


def test_naturalsize_rounding_steps_up_decimal():
    assert naturalsize(999999) == "1.0 MB"
    assert naturalsize(-999999) == "-1.0 MB"
    assert naturalsize(999999999) == "1.0 GB"


def test_naturalsize_no_step_up_when_rounding_stays_below_base():
    assert naturalsize(999949) == "999.9 kB"
    assert naturalsize(999000) == "999.0 kB"


def test_naturalsize_rounding_steps_up_binary():
    assert naturalsize(1048575, binary=True) == "1.0 MiB"
    assert naturalsize(-1048575, binary=True) == "-1.0 MiB"


def test_naturalsize_rounding_steps_up_gnu():
    assert naturalsize(1048575, gnu=True) == "1.0M"
    assert naturalsize(-1048575, gnu=True) == "-1.0M"


def test_naturalsize_rounding_steps_up_to_last_suffix():
    assert naturalsize(999999 * 10**24) == "1.0 QB"


def test_naturalsize_rounding_with_custom_format():
    assert naturalsize(999500, format="%.0f") == "1 MB"
    assert naturalsize(999400, format="%.0f") == "999 kB"


@pytest.mark.parametrize(
    "fmt, expected",
    [
        ("%.0f", "3 kB"),
        ("%.1f", "3.0 kB"),
        ("%.2f", "3.00 kB"),
        ("%.3f", "3.000 kB"),
        ("%d", "3 kB"),
        ("%5.1f", "  3.0 kB"),
    ],
)
def test_naturalsize_custom_format(fmt, expected):
    assert naturalsize(3000, format=fmt) == expected


def test_naturalsize_custom_format_does_not_affect_bytes():
    assert naturalsize(300, format="%.3f") == "300 Bytes"
    assert naturalsize(1, format="%.3f") == "1 Byte"
    assert naturalsize(300, gnu=True, format="%.3f") == "300B"


def test_naturalsize_gnu_ignores_binary_flag():
    assert naturalsize(3000, True, True) == naturalsize(3000, False, True)
    assert naturalsize(3000, binary=True, gnu=True) == "2.9K"


def test_naturalsize_binary_differs_from_decimal():
    assert naturalsize(1024) == "1.0 kB"
    assert naturalsize(1024, binary=True) == "1.0 KiB"
    assert naturalsize(1000, binary=True) == "1000 Bytes"


@pytest.mark.parametrize(
    "value, expected",
    [
        ("300", "300 Bytes"),
        ("1", "1 Byte"),
        ("1.0", "1 Byte"),
        ("3000", "3.0 kB"),
        ("-3000", "-3.0 kB"),
        (" 3000 ", "3.0 kB"),
        ("3e6", "3.0 MB"),
    ],
)
def test_naturalsize_string_values(value, expected):
    assert naturalsize(value) == expected


def test_naturalsize_string_values_binary_and_gnu():
    assert naturalsize("3000", binary=True) == "2.9 KiB"
    assert naturalsize("3000", gnu=True) == "2.9K"
    assert naturalsize("300", gnu=True) == "300B"


@pytest.mark.parametrize("bad", ["abc", "", "1,000", "12 kB"])
def test_naturalsize_invalid_string_raises_value_error(bad):
    with pytest.raises(ValueError):
        naturalsize(bad)


@pytest.mark.parametrize("bad", [None, [1], {"a": 1}, (1,), object()])
def test_naturalsize_invalid_type_raises_type_error(bad):
    with pytest.raises(TypeError):
        naturalsize(bad)


def test_naturalsize_nan_raises_value_error():
    with pytest.raises(ValueError):
        naturalsize(float("nan"))


def test_naturalsize_infinity():
    assert naturalsize(float("inf")) == "inf QB"
    assert naturalsize(float("-inf")) == "-inf QB"


def test_naturalsize_invalid_format_raises():
    with pytest.raises(TypeError):
        naturalsize(3000, format="no placeholder")
    with pytest.raises(ValueError):
        naturalsize(3000, format="%z")


def test_naturalsize_huge_integer_value():
    assert naturalsize(10**40) == "10000000000.0 QB"


def test_naturalsize_return_type_is_str():
    for kwargs in ({}, {"binary": True}, {"gnu": True}):
        for value in (0, 1, 500, 5000, 5 * 10**9):
            assert isinstance(naturalsize(value, **kwargs), str)


def test_naturalsize_uses_gettext_for_bytes(monkeypatch):
    monkeypatch.setattr(filesize, "_", lambda message: message + "!")
    assert naturalsize(5) == "5 Bytes!"
    assert naturalsize(1) == "1 Byte!"
    assert naturalsize(-1) == "-1 Byte!"


def test_naturalsize_uses_gettext_for_suffix(monkeypatch):
    monkeypatch.setattr(filesize, "_", lambda message: message + "!")
    assert naturalsize(3000) == "3.0 kB!"
    assert naturalsize(3000, binary=True) == "2.9 KiB!"
    assert naturalsize(3000, gnu=True) == "2.9K!"


def test_naturalsize_gnu_bytes_not_translated(monkeypatch):
    monkeypatch.setattr(filesize, "_", lambda message: message + "!")
    assert naturalsize(300, gnu=True) == "300B"
    assert naturalsize(1, gnu=True) == "1B"