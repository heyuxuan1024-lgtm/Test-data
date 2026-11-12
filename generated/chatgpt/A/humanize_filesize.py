
import math
import pytest

from humanize.filesize import naturalsize, suffixes


@pytest.mark.parametrize(
    "value, expected",
    [
        (0, "0 Bytes"),
        (1, "1 Byte"),
        (-1, "-1 Byte"),
        (10, "10 Bytes"),
        (-10, "-10 Bytes"),
        (999, "999 Bytes"),
        (-999, "-999 Bytes"),
        (1000, "1.0 kB"),
        (1500, "1.5 kB"),
        (3000000, "3.0 MB"),
        (1000000000, "1.0 GB"),
        (1000000000000, "1.0 TB"),
    ],
)
def test_naturalsize_decimal(value, expected):
    assert naturalsize(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (0, "0 Bytes"),
        (1, "1 Byte"),
        (-1, "-1 Byte"),
        (1023, "1023 Bytes"),
        (-1023, "-1023 Bytes"),
        (1024, "1.0 KiB"),
        (2048, "2.0 KiB"),
        (1536, "1.5 KiB"),
        (1048576, "1.0 MiB"),
        (1073741824, "1.0 GiB"),
        (1099511627776, "1.0 TiB"),
    ],
)
def test_naturalsize_binary(value, expected):
    assert naturalsize(value, binary=True) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (0, "0B"),
        (1, "1B"),
        (-1, "-1B"),
        (1023, "1023B"),
        (-1023, "-1023B"),
        (1024, "1.0K"),
        (2048, "2.0K"),
        (1536, "1.5K"),
        (1048576, "1.0M"),
        (1073741824, "1.0G"),
        (1099511627776, "1.0T"),
    ],
)
def test_naturalsize_gnu(value, expected):
    assert naturalsize(value, gnu=True) == expected


def test_gnu_ignores_binary_argument():
    assert naturalsize(1024, binary=True, gnu=True) == "1.0K"
    assert naturalsize(1000, binary=False, gnu=True) == "1000B"


def test_binary_and_decimal_differ():
    assert naturalsize(1000) == "1.0 kB"
    assert naturalsize(1000, binary=True) == "1000 Bytes"


def test_string_integer_input():
    assert naturalsize("1000") == "1.0 kB"


def test_string_float_input():
    assert naturalsize("1500.5") == "1.5 kB"


def test_float_input():
    assert naturalsize(1500.5) == "1.5 kB"


def test_negative_float_input():
    assert naturalsize(-1500.5) == "-1.5 kB"


def test_custom_format():
    assert naturalsize(3000, format="%.3f") == "3.000 kB"
    assert naturalsize(3000, binary=True, format="%.3f") == "2.930 KiB"
    assert naturalsize(3000, gnu=True, format="%.3f") == "2.930K"


def test_custom_integer_format():
    assert naturalsize(1500, format="%.0f") == "2 kB"


def test_custom_format_for_bytes():
    assert naturalsize(500, format="%.3f") == "500 Bytes"


def test_decimal_rounding_suffix_transition():
    assert naturalsize(999999) == "1.0 MB"


def test_binary_rounding_suffix_transition():
    assert naturalsize(1024**2 - 1, binary=True) == "1.0 MiB"


def test_gnu_rounding_suffix_transition():
    assert naturalsize(1024**2 - 1, gnu=True) == "1.0M"


@pytest.mark.parametrize(
    "value, expected",
    [
        (999499, "999.5 kB"),
        (999500, "999.5 kB"),
        (999949, "999.9 kB"),
        (999999, "1.0 MB"),
        (1000000, "1.0 MB"),
        (999999999, "1.0 GB"),
    ],
)
def test_decimal_boundary_values(value, expected):
    assert naturalsize(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (1023, "1023 Bytes"),
        (1024, "1.0 KiB"),
        (1048575, "1.0 MiB"),
        (1048576, "1.0 MiB"),
        (1073741823, "1.0 GiB"),
        (1073741824, "1.0 GiB"),
    ],
)
def test_binary_boundary_values(value, expected):
    assert naturalsize(value, binary=True) == expected


def test_large_decimal_values():
    assert naturalsize(10**15) == "1.0 PB"
    assert naturalsize(10**18) == "1.0 EB"
    assert naturalsize(10**21) == "1.0 ZB"
    assert naturalsize(10**24) == "1.0 YB"
    assert naturalsize(10**27) == "1.0 RB"
    assert naturalsize(10**28) == "10.0 RB"


def test_very_large_decimal_values():
    assert naturalsize(10**30) == "1000.0 RB"
    assert naturalsize(3 * 10**34) == "30000.0 QB"


def test_large_binary_values():
    assert naturalsize(1024**5, binary=True) == "1.0 PiB"
    assert naturalsize(1024**6, binary=True) == "1.0 EiB"
    assert naturalsize(1024**7, binary=True) == "1.0 ZiB"
    assert naturalsize(1024**8, binary=True) == "1.0 YiB"
    assert naturalsize(1024**9, binary=True) == "1.0 RiB"
    assert naturalsize(1024**10, binary=True) == "1.0 QiB"


def test_large_gnu_values():
    assert naturalsize(1024**5, gnu=True) == "1.0P"
    assert naturalsize(1024**6, gnu=True) == "1.0E"
    assert naturalsize(1024**7, gnu=True) == "1.0Z"
    assert naturalsize(1024**8, gnu=True) == "1.0Y"
    assert naturalsize(1024**9, gnu=True) == "1.0R"
    assert naturalsize(1024**10, gnu=True) == "1.0Q"


def test_suffix_dictionary():
    assert suffixes["decimal"] == (
        "kB", "MB", "GB", "TB", "PB",
        "EB", "ZB", "YB", "RB", "QB",
    )
    assert suffixes["binary"] == (
        "KiB", "MiB", "GiB", "TiB", "PiB",
        "EiB", "ZiB", "YiB", "RiB", "QiB",
    )
    assert suffixes["gnu"] == "KMGTPEZYRQ"


def test_fractional_values_below_base():
    assert naturalsize(0.9) == "0 Bytes"
    assert naturalsize(-0.9) == "0 Bytes"
    assert naturalsize(999.9) == "999 Bytes"


def test_exact_base_powers():
    for exponent, suffix in enumerate(suffixes["decimal"], start=1):
        assert naturalsize(1000**exponent) == f"1.0 {suffix}"


def test_exact_binary_base_powers():
    for exponent, suffix in enumerate(suffixes["binary"], start=1):
        assert naturalsize(1024**exponent, binary=True) == f"1.0 {suffix}"


def test_exact_gnu_base_powers():
    for exponent, suffix in enumerate(suffixes["gnu"], start=1):
        assert naturalsize(1024**exponent, gnu=True) == f"1.0{suffix}"


def test_custom_format_large_precision():
    assert naturalsize(1234567, format="%.4f") == "1.2346 MB"


def test_custom_format_rounding_up():
    assert naturalsize(999999, format="%.0f") == "1 MB"


def test_custom_format_rounding_down():
    assert naturalsize(1000000, format="%.0f") == "1 MB"


@pytest.mark.parametrize(
    "value",
    [
        None,
        [],
        {},
        object(),
    ],
)
def test_invalid_value_type(value):
    with pytest.raises((TypeError, ValueError)):
        naturalsize(value)


@pytest.mark.parametrize(
    "value",
    [
        "not a number",
        "",
        " ",
        "abc123",
    ],
)
def test_invalid_string_value(value):
    with pytest.raises(ValueError):
        naturalsize(value)


def test_nan_value():
    with pytest.raises((ValueError, OverflowError)):
        naturalsize(float("nan"))


@pytest.mark.parametrize(
    "value",
    [
        float("inf"),
        float("-inf"),
    ],
)
def test_infinite_values(value):
    with pytest.raises((OverflowError, ValueError)):
        naturalsize(value)


def test_invalid_format_string():
    with pytest.raises((TypeError, ValueError)):
        naturalsize(1000, format="invalid")


def test_format_missing_conversion():
    with pytest.raises(TypeError):
        naturalsize(1000, format="%.2f %s")


def test_format_multiple_conversions():
    with pytest.raises(TypeError):
        naturalsize(1000, format="%.2f %.2f")


def test_format_non_string():
    with pytest.raises(TypeError):
        naturalsize(1000, format=None)


def test_format_integer_conversion():
    assert naturalsize(1500, format="%d") == "2 kB"


def test_format_percent_literal():
    assert naturalsize(1500, format="%.1f%%") == "1.5% kB"


def test_negative_large_binary_value():
    assert naturalsize(-4096, binary=True) == "-4.0 KiB"


def test_negative_large_gnu_value():
    assert naturalsize(-2048, gnu=True) == "-2.0K"


def test_negative_large_decimal_value():
    assert naturalsize(-3000000) == "-3.0 MB"


def test_boolean_values():
    assert naturalsize(True) == "1 Byte"
    assert naturalsize(False) == "0 Bytes"


def test_boolean_gnu_values():
    assert naturalsize(True, gnu=True) == "1B"
    assert naturalsize(False, gnu=True) == "0B"


def test_binary_one_byte():
    assert naturalsize(1, binary=True) == "1 Byte"


def test_gnu_one_byte():
    assert naturalsize(1, gnu=True) == "1B"


def test_decimal_small_negative_fraction():
    assert naturalsize(-0.5) == "0 Bytes"


def test_rounding_to_larger_suffix_with_negative_value():
    assert naturalsize(-999999) == "-1.0 MB"


def test_rounding_to_larger_suffix_with_custom_format():
    assert naturalsize(999999, format="%.0f") == "1 MB"


def test_gnu_format_without_space():
    assert naturalsize(2048, gnu=True) == "2.0K"


def test_binary_format_with_space():
    assert naturalsize(2048, binary=True) == "2.0 KiB"


def test_decimal_format_with_space():
    assert naturalsize(2048) == "2.0 kB"


def test_suffix_limit_decimal():
    assert naturalsize(10**40) == "10000000000000000.0 QB"


def test_suffix_limit_binary():
    assert naturalsize(1024**20, binary=True) == "1024.0 QiB"


def test_suffix_limit_gnu():
    assert naturalsize(1024**20, gnu=True) == "1024.0Q"
