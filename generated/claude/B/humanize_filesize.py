import pytest

from humanize import filesize


def test_suffixes_structure():
    assert set(filesize.suffixes) == {"decimal", "binary", "gnu"}
    assert len(filesize.suffixes["decimal"]) == 10
    assert len(filesize.suffixes["binary"]) == 10
    assert len(filesize.suffixes["gnu"]) == 10
    assert filesize.suffixes["decimal"][0] == "kB"
    assert filesize.suffixes["decimal"][-1] == "QB"
    assert filesize.suffixes["binary"][0] == "KiB"
    assert filesize.suffixes["binary"][-1] == "QiB"
    assert filesize.suffixes["gnu"] == "KMGTPEZYRQ"


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
    assert filesize.naturalsize(value) == expected


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
    assert filesize.naturalsize(value, binary=True) == expected


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
    assert filesize.naturalsize(value, gnu=True) == expected


def test_naturalsize_docstring_examples():
    assert filesize.naturalsize(3000000) == "3.0 MB"
    assert filesize.naturalsize(300, False, True) == "300B"
    assert filesize.naturalsize(3000, False, True) == "2.9K"
    assert filesize.naturalsize(3000, False, True, "%.3f") == "2.930K"
    assert filesize.naturalsize(3000, True) == "2.9 KiB"
    assert filesize.naturalsize(10**28) == "10.0 RB"
    assert filesize.naturalsize(10**34 * 3) == "30000.0 QB"
    assert filesize.naturalsize(-4096, True) == "-4.0 KiB"


def test_naturalsize_decimal_boundaries():
    assert filesize.naturalsize(1000) == "1.0 kB"
    assert filesize.naturalsize(1500) == "1.5 kB"
    assert filesize.naturalsize(-1500) == "-1.5 kB"
    assert filesize.naturalsize(3000) == "3.0 kB"
    assert filesize.naturalsize(3000.5) == "3.0 kB"


def test_naturalsize_binary_boundaries():
    assert filesize.naturalsize(1024, binary=True) == "1.0 KiB"
    assert filesize.naturalsize(1536, binary=True) == "1.5 KiB"
    assert filesize.naturalsize(3 * 1024**2, binary=True) == "3.0 MiB"


def test_naturalsize_gnu_boundaries():
    assert filesize.naturalsize(1024, gnu=True) == "1.0K"
    assert filesize.naturalsize(1536, gnu=True) == "1.5K"
    assert filesize.naturalsize(3 * 1024**2, gnu=True) == "3.0M"
    assert filesize.naturalsize(-1536, gnu=True) == "-1.5K"


@pytest.mark.parametrize("n", range(1, 11))
def test_naturalsize_every_decimal_suffix(n):
    name = filesize.suffixes["decimal"][n - 1]
    assert filesize.naturalsize(3 * 1000**n) == f"3.0 {name}"
    assert filesize.naturalsize(-3 * 1000**n) == f"-3.0 {name}"


@pytest.mark.parametrize("n", range(1, 11))
def test_naturalsize_every_binary_suffix(n):
    name = filesize.suffixes["binary"][n - 1]
    assert filesize.naturalsize(3 * 1024**n, binary=True) == f"3.0 {name}"
    assert filesize.naturalsize(-3 * 1024**n, binary=True) == f"-3.0 {name}"


@pytest.mark.parametrize("n", range(1, 11))
def test_naturalsize_every_gnu_suffix(n):
    name = filesize.suffixes["gnu"][n - 1]
    assert filesize.naturalsize(3 * 1024**n, gnu=True) == f"3.0{name}"
    assert filesize.naturalsize(-3 * 1024**n, gnu=True) == f"-3.0{name}"


def test_naturalsize_largest_suffix_is_capped():
    assert filesize.naturalsize(3 * 1000**11) == "3000.0 QB"
    assert filesize.naturalsize(3 * 1000**12) == "3000000.0 QB"
    assert filesize.naturalsize(3 * 1024**11, binary=True) == "3072.0 QiB"
    assert filesize.naturalsize(3 * 1024**11, gnu=True) == "3072.0Q"


def test_naturalsize_rounding_steps_up_decimal():
    assert filesize.naturalsize(999999) == "1.0 MB"
    assert filesize.naturalsize(-999999) == "-1.0 MB"
    assert filesize.naturalsize(999999999) == "1.0 GB"


def test_naturalsize_no_step_up_when_rounding_stays_below_base():
    assert filesize.naturalsize(999949) == "999.9 kB"
    assert filesize.naturalsize(999000) == "999.0 kB"


def test_naturalsize_rounding_steps_up_binary():
    assert filesize.naturalsize(1048575, binary=True) == "1.0 MiB"
    assert filesize.naturalsize(-1048575, binary=True) == "-1.0 MiB"


def test_naturalsize_rounding_steps_up_gnu():
    assert filesize.naturalsize(1048575, gnu=True) == "1.0M"
    assert filesize.naturalsize(-1048575, gnu=True) == "-1.0M"


def test_naturalsize_rounding_with_custom_format():
    assert filesize.naturalsize(999500, format="%.0f") == "1 MB"
    assert filesize.naturalsize(999400, format="%.0f") == "999 kB"


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
    assert filesize.naturalsize(3000, format=fmt) == expected


def test_naturalsize_custom_format_does_not_affect_bytes():
    assert filesize.naturalsize(300, format="%.3f") == "300 Bytes"
    assert filesize.naturalsize(1, format="%.3f") == "1 Byte"
    assert filesize.naturalsize(300, gnu=True, format="%.3f") == "300B"


def test_naturalsize_gnu_ignores_binary_flag():
    assert filesize.naturalsize(3000, True, True) == filesize.naturalsize(3000, False, True)
    assert filesize.naturalsize(3000, binary=True, gnu=True) == "2.9K"


def test_naturalsize_binary_differs_from_decimal():
    assert filesize.naturalsize(1024) == "1.0 kB"
    assert filesize.naturalsize(1024, binary=True) == "1.0 KiB"
    assert filesize.naturalsize(1000, binary=True) == "1000 Bytes"


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
    assert filesize.naturalsize(value) == expected


def test_naturalsize_string_values_binary_and_gnu():
    assert filesize.naturalsize("3000", binary=True) == "2.9 KiB"
    assert filesize.naturalsize("3000", gnu=True) == "2.9K"
    assert filesize.naturalsize("300", gnu=True) == "300B"


@pytest.mark.parametrize("bad", ["abc", "", "1,000", "12 kB"])
def test_naturalsize_invalid_string_raises_value_error(bad):
    with pytest.raises(ValueError):
        filesize.naturalsize(bad)


@pytest.mark.parametrize("bad", [None, [1], {"a": 1}, (1,), object()])
def test_naturalsize_invalid_type_raises_type_error(bad):
    with pytest.raises(TypeError):
        filesize.naturalsize(bad)


def test_naturalsize_nan_raises_value_error():
    with pytest.raises(ValueError):
        filesize.naturalsize(float("nan"))


def test_naturalsize_infinity_raises_overflow_error():
    with pytest.raises(OverflowError):
        filesize.naturalsize(float("inf"))
    with pytest.raises(OverflowError):
        filesize.naturalsize(float("-inf"))


def test_naturalsize_invalid_format_raises():
    with pytest.raises(TypeError):
        filesize.naturalsize(3000, format="no placeholder")
    with pytest.raises(ValueError):
        filesize.naturalsize(3000, format="%z")


def test_naturalsize_huge_integer_value():
    assert filesize.naturalsize(10**40) == "10000000000.0 QB"


def test_naturalsize_return_type_is_str():
    for kwargs in ({}, {"binary": True}, {"gnu": True}):
        for value in (0, 1, 500, 5000, 5 * 10**9):
            assert isinstance(filesize.naturalsize(value, **kwargs), str)


def test_naturalsize_uses_gettext_for_bytes(monkeypatch):
    monkeypatch.setattr(filesize, "_", lambda message: message + "!")
    assert filesize.naturalsize(5) == "5 Bytes!"
    assert filesize.naturalsize(1) == "1 Byte!"
    assert filesize.naturalsize(-1) == "-1 Byte!"


def test_naturalsize_uses_gettext_for_suffix(monkeypatch):
    monkeypatch.setattr(filesize, "_", lambda message: message + "!")
    assert filesize.naturalsize(3000) == "3.0 kB!"
    assert filesize.naturalsize(3000, binary=True) == "2.9 KiB!"
    assert filesize.naturalsize(3000, gnu=True) == "2.9K!"


def test_naturalsize_gnu_bytes_not_translated(monkeypatch):
    monkeypatch.setattr(filesize, "_", lambda message: message + "!")
    assert filesize.naturalsize(300, gnu=True) == "300B"
    assert filesize.naturalsize(1, gnu=True) == "1B"