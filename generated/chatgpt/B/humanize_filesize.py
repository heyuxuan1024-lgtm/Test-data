
import math

import pytest
from humanize import filesize


def test_suffixes():
    assert filesize.suffixes["decimal"] == (
        "kB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB", "RB", "QB"
    )
    assert filesize.suffixes["binary"] == (
        "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB", "RiB", "QiB"
    )
    assert filesize.suffixes["gnu"] == "KMGTPEZYRQ"


@pytest.mark.parametrize(
    "value, expected",
    [
        (0, "0 Bytes"),
        (1, "1 Byte"),
        (-1, "-1 Byte"),
        (2, "2 Bytes"),
        (-2, "-2 Bytes"),
        (999, "999 Bytes"),
        (-999, "-999 Bytes"),
        (999.9, "999 Bytes"),
        (-999.9, "-999 Bytes"),
        (1000, "1.0 kB"),
        (1500, "1.5 kB"),
        (1000000, "1.0 MB"),
        (3000000, "3.0 MB"),
        (1000000000, "1.0 GB"),
        (1000000000000, "1.0 TB"),
    ],
)
def test_naturalsize_decimal(value, expected):
    assert filesize.naturalsize(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (0, "0 Bytes"),
        (1, "1 Byte"),
        (-1, "-1 Byte"),
        (2, "2 Bytes"),
        (1023, "1023 Bytes"),
        (-1023, "-1023 Bytes"),
        (1024, "1.0 KiB"),
        (1536, "1.5 KiB"),
        (1048576, "1.0 MiB"),
        (3145728, "3.0 MiB"),
        (1073741824, "1.0 GiB"),
        (1099511627776, "1.0 TiB"),
    ],
)
def test_naturalsize_binary(value, expected):
    assert filesize.naturalsize(value, binary=True) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (0, "0B"),
        (1, "1B"),
        (-1, "-1B"),
        (2, "2B"),
        (1023, "1023B"),
        (-1023, "-1023B"),
        (1024, "1.0K"),
        (1536, "1.5K"),
        (1048576, "1.0M"),
        (3145728, "3.0M"),
        (1073741824, "1.0G"),
        (1099511627776, "1.0T"),
    ],
)
def test_naturalsize_gnu(value, expected):
    assert filesize.naturalsize(value, gnu=True) == expected


def test_gnu_ignores_binary_argument():
    assert filesize.naturalsize(1000, binary=True, gnu=True) == "1000B"
    assert filesize.naturalsize(1024, binary=True, gnu=True) == "1.0K"


@pytest.mark.parametrize(
    "value, expected",
    [
        ("0", "0 Bytes"),
        ("1", "1 Byte"),
        ("-1", "-1 Byte"),
        ("1000", "1.0 kB"),
        ("1500.5", "1.5 kB"),
        ("1048576", "1.0 MB"),
        ("1e6", "1.0 MB"),
        ("1.5e3", "1.5 kB"),
    ],
)
def test_naturalsize_string_values(value, expected):
    assert filesize.naturalsize(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (0.5, "0 Bytes"),
        (-0.5, "0 Bytes"),
        (1.5, "1 Bytes"),
        (-1.5, "-1 Bytes"),
        (999.9, "999 Bytes"),
        (1000.5, "1.0 kB"),
        (1500.5, "1.5 kB"),
        (1999.9, "2.0 kB"),
    ],
)
def test_naturalsize_float_values(value, expected):
    assert filesize.naturalsize(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (999999, "1.0 MB"),
        (999499, "999.5 kB"),
        (999500, "999.5 kB"),
        (999999999, "1.0 GB"),
        (1023999, "1.0 MiB"),
    ],
)
def test_rounding_boundary_decimal(value, expected):
    assert filesize.naturalsize(value) == expected


def test_rounding_boundary_binary():
    assert filesize.naturalsize(1023 * 1024, binary=True) == "1023.0 KiB"
    assert filesize.naturalsize(1023.999 * 1024, binary=True) == "1.0 MiB"


@pytest.mark.parametrize(
    "value, expected",
    [
        (300, "300B"),
        (1023, "1023B"),
        (1024, "1.0K"),
        (3000, "2.9K"),
        (1536, "1.5K"),
        (1048576, "1.0M"),
    ],
)
def test_gnu_examples(value, expected):
    assert filesize.naturalsize(value, gnu=True) == expected


def test_custom_format():
    assert filesize.naturalsize(3000, format="%.3f") == "3.000 kB"
    assert filesize.naturalsize(3000, gnu=True, format="%.3f") == "2.930K"
    assert filesize.naturalsize(3000, binary=True, format="%.2f") == "2.93 KiB"
    assert filesize.naturalsize(1000, format="%d") == "1 kB"
    assert filesize.naturalsize(1000, format="%.0f") == "1 kB"


def test_custom_format_rounding_can_change_suffix():
    assert filesize.naturalsize(999999, format="%.0f") == "1 MB"
    assert filesize.naturalsize(999999, format="%.2f") == "1000.00 kB"
    assert filesize.naturalsize(1023 * 1024, binary=True, format="%.0f") == "1 MiB"


@pytest.mark.parametrize(
    "value",
    [
        "invalid",
        "abc",
        "",
        " ",
        None,
        object(),
        [],
        {},
    ],
)
def test_invalid_values_raise(value):
    with pytest.raises((TypeError, ValueError)):
        filesize.naturalsize(value)


@pytest.mark.parametrize(
    "value",
    [
        float("nan"),
        float("inf"),
        float("-inf"),
    ],
)
def test_non_finite_values_raise(value):
    with pytest.raises((ValueError, OverflowError)):
        filesize.naturalsize(value)


@pytest.mark.parametrize(
    "format_string",
    [
        "%",
        "%s",
        "%d",
        "%f %f",
        "invalid",
        "{:.1f}",
        None,
        123,
    ],
)
def test_invalid_format_strings(format_string):
    with pytest.raises((TypeError, ValueError)):
        filesize.naturalsize(1000, format=format_string)


def test_invalid_format_string_not_used_for_small_values():
    assert filesize.naturalsize(10, format="%") == "10 Bytes"
    assert filesize.naturalsize(1, format="%") == "1 Byte"


@pytest.mark.parametrize(
    "value, expected",
    [
        (10**3, "1.0 kB"),
        (10**6, "1.0 MB"),
        (10**9, "1.0 GB"),
        (10**12, "1.0 TB"),
        (10**15, "1.0 PB"),
        (10**18, "1.0 EB"),
        (10**21, "1.0 ZB"),
        (10**24, "1.0 YB"),
        (10**27, "1.0 RB"),
        (10**30, "1.0 QB"),
    ],
)
def test_all_decimal_suffixes(value, expected):
    assert filesize.naturalsize(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (2**10, "1.0 KiB"),
        (2**20, "1.0 MiB"),
        (2**30, "1.0 GiB"),
        (2**40, "1.0 TiB"),
        (2**50, "1.0 PiB"),
        (2**60, "1.0 EiB"),
        (2**70, "1.0 ZiB"),
        (2**80, "1.0 YiB"),
        (2**90, "1.0 RiB"),
        (2**100, "1.0 QiB"),
    ],
)
def test_all_binary_suffixes(value, expected):
    assert filesize.naturalsize(value, binary=True) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (2**10, "1.0K"),
        (2**20, "1.0M"),
        (2**30, "1.0G"),
        (2**40, "1.0T"),
        (2**50, "1.0P"),
        (2**60, "1.0E"),
        (2**70, "1.0Z"),
        (2**80, "1.0Y"),
        (2**90, "1.0R"),
        (2**100, "1.0Q"),
    ],
)
def test_all_gnu_suffixes(value, expected):
    assert filesize.naturalsize(value, gnu=True) == expected


def test_values_beyond_largest_decimal_suffix():
    assert filesize.naturalsize(10**33) == "1000.0 QB"
    assert filesize.naturalsize(3 * 10**34) == "30000.0 QB"


def test_values_beyond_largest_binary_suffix():
    assert filesize.naturalsize(2**110, binary=True) == "1024.0 QiB"
    assert filesize.naturalsize(2**120, binary=True) == "1048576.0 QiB"


def test_values_beyond_largest_gnu_suffix():
    assert filesize.naturalsize(2**110, gnu=True) == "1024.0Q"


def test_negative_large_values():
    assert filesize.naturalsize(-4096) == "-4.1 kB"
    assert filesize.naturalsize(-4096, binary=True) == "-4.0 KiB"
    assert filesize.naturalsize(-4096, gnu=True) == "-4.0K"


def test_negative_values_rounding_boundary():
    assert filesize.naturalsize(-999999) == "-1.0 MB"
    assert filesize.naturalsize(-1023 * 1024, binary=True) == "-1.0 MiB"


def test_formatting_preserves_sign():
    assert filesize.naturalsize(-1500, format="%.2f") == "-1.50 kB"
    assert filesize.naturalsize(-1536, binary=True, format="%.2f") == "-1.50 KiB"
    assert filesize.naturalsize(-1536, gnu=True, format="%.2f") == "-1.50K"


def test_boolean_values():
    assert filesize.naturalsize(True) == "1 Byte"
    assert filesize.naturalsize(False) == "0 Bytes"


def test_very_small_float_values():
    assert filesize.naturalsize(0.001) == "0 Bytes"
    assert filesize.naturalsize(-0.001) == "0 Bytes"


def test_large_integer_value():
    value = 10**100
    result = filesize.naturalsize(value)
    assert result.endswith(" QB")
    assert float(result.split()[0]) > 0


def test_large_negative_integer_value():
    value = -(10**100)
    result = filesize.naturalsize(value)
    assert result.startswith("-")
    assert result.endswith(" QB")


def test_format_with_width_and_precision():
    assert filesize.naturalsize(1500, format="%10.2f") == "      1.50 kB"
    assert filesize.naturalsize(1500, gnu=True, format="%08.2f") == "0001.46K"


def test_format_with_percent_literal():
    assert filesize.naturalsize(1500, format="%.1f%%") == "1.5% kB"


def test_binary_and_decimal_differ():
    assert filesize.naturalsize(1000000) == "1.0 MB"
    assert filesize.naturalsize(1000000, binary=True) == "976.6 KiB"


def test_decimal_boundary_values():
    assert filesize.naturalsize(999) == "999 Bytes"
    assert filesize.naturalsize(1000) == "1.0 kB"
    assert filesize.naturalsize(-999) == "-999 Bytes"
    assert filesize.naturalsize(-1000) == "-1.0 kB"


def test_binary_boundary_values():
    assert filesize.naturalsize(1023, binary=True) == "1023 Bytes"
    assert filesize.naturalsize(1024, binary=True) == "1.0 KiB"
    assert filesize.naturalsize(-1023, binary=True) == "-1023 Bytes"
    assert filesize.naturalsize(-1024, binary=True) == "-1.0 KiB"


def test_gnu_boundary_values():
    assert filesize.naturalsize(1023, gnu=True) == "1023B"
    assert filesize.naturalsize(1024, gnu=True) == "1.0K"
    assert filesize.naturalsize(-1023, gnu=True) == "-1023B"
    assert filesize.naturalsize(-1024, gnu=True) == "-1.0K"


def test_decimal_singular_byte_with_fraction():
    assert filesize.naturalsize(1.9) == "1 Byte"
    assert filesize.naturalsize(-1.9) == "-1 Byte"


def test_binary_singular_byte_with_fraction():
    assert filesize.naturalsize(1.9, binary=True) == "1 Byte"
    assert filesize.naturalsize(-1.9, binary=True) == "-1 Byte"


def test_gnu_does_not_use_singular_byte_translation():
    assert filesize.naturalsize(1, gnu=True) == "1B"
    assert filesize.naturalsize(-1, gnu=True) == "-1B"


def test_suffix_selection_uses_unrounded_value():
    assert filesize.naturalsize(999950, format="%.1f") == "1000.0 kB"
    assert filesize.naturalsize(999999, format="%.1f") == "1.0 MB"


def test_format_that_rounds_to_base_steps_up_suffix():
    assert filesize.naturalsize(999999, format="%.0f") == "1 MB"
    assert filesize.naturalsize(1023999, binary=True, format="%.0f") == "1 MiB"


def test_format_that_rounds_below_base_does_not_step_up():
    assert filesize.naturalsize(999499, format="%.0f") == "999 kB"
    assert filesize.naturalsize(1023 * 1024, binary=True, format="%.0f") == "1023 KiB"


def test_custom_format_rounding_with_negative_value():
    assert filesize.naturalsize(-999999, format="%.0f") == "-1 MB"
    assert filesize.naturalsize(-1023999, binary=True, format="%.0f") == "-1 MiB"


def test_format_string_with_multiple_numeric_specifiers_raises():
    with pytest.raises((TypeError, ValueError)):
        filesize.naturalsize(1000, format="%.1f %.1f")


def test_format_string_with_mapping_specifier_raises():
    with pytest.raises((TypeError, ValueError)):
        filesize.naturalsize(1000, format="%(value).1f")


def test_format_string_with_integer_conversion():
    assert filesize.naturalsize(1000, format="%d") == "1 kB"


def test_translation_function_is_used_for_byte_labels(monkeypatch):
    monkeypatch.setattr(filesize, "_", lambda value: "translated:" + value)
    assert filesize.naturalsize(1) == "translated:1 Byte"
    assert filesize.naturalsize(10) == "translated:10 Bytes"


def test_translation_function_is_used_for_suffixes(monkeypatch):
    monkeypatch.setattr(filesize, "_", lambda value: "translated:" + value)
    assert filesize.naturalsize(1000) == "1.0 translated:kB"
    assert filesize.naturalsize(1024, binary=True) == "1.0 translated:KiB"


def test_gnu_suffix_translation():
    assert filesize.naturalsize(1024, gnu=True) == "1.0K"


def test_module_lazy_modules():
    assert "humanize.i18n" in filesize.__lazy_modules__
    assert "math" in filesize.__lazy_modules__


def test_suffix_selection_at_large_decimal_boundary():
    assert filesize.naturalsize(10**30 - 1) == "1000.0 QB"
    assert filesize.naturalsize(10**30) == "1.0 QB"


def test_suffix_selection_at_large_binary_boundary():
    assert filesize.naturalsize(2**100 - 1, binary=True) == "1024.0 QiB"
    assert filesize.naturalsize(2**100, binary=True) == "1.0 QiB"


def test_suffix_selection_at_large_gnu_boundary():
    assert filesize.naturalsize(2**90 - 1, gnu=True) == "1024.0R"
    assert filesize.naturalsize(2**90, gnu=True) == "1.0Q"


def test_custom_format_integer_and_float_inputs_match():
    assert filesize.naturalsize(1536, binary=True, format="%.3f") == "1.500 KiB"
    assert filesize.naturalsize(1536.0, binary=True, format="%.3f") == "1.500 KiB"


def test_decimal_suffix_selection_around_base():
    assert filesize.naturalsize(999999) == "1.0 MB"
    assert filesize.naturalsize(1000000) == "1.0 MB"
    assert filesize.naturalsize(1000001) == "1.0 MB"


def test_binary_suffix_selection_around_base():
    assert filesize.naturalsize(1048575, binary=True) == "1.0 MiB"
    assert filesize.naturalsize(1048576, binary=True) == "1.0 MiB"
    assert filesize.naturalsize(1048577, binary=True) == "1.0 MiB"


def test_gnu_suffix_selection_around_base():
    assert filesize.naturalsize(1024**2 - 1, gnu=True) == "1.0M"
    assert filesize.naturalsize(1024**2, gnu=True) == "1.0M"
    assert filesize.naturalsize(1024**2 + 1, gnu=True) == "1.0M"


def test_negative_zero():
    assert filesize.naturalsize(-0.0) == "0 Bytes"
    assert filesize.naturalsize(-0.0, gnu=True) == "0B"


def test_extremely_large_float():
    value = 1e300
    result = filesize.naturalsize(value)
    assert result.endswith(" QB")


def test_extremely_small_exponent_string():
    assert filesize.naturalsize("1e-100") == "0 Bytes"


def test_scientific_notation_string():
    assert filesize.naturalsize("1e3") == "1.0 kB"
    assert filesize.naturalsize("1e6") == "1.0 MB"


def test_binary_gnu_precedence():
    assert filesize.naturalsize(1024, binary=True, gnu=True) == "1.0K"
    assert filesize.naturalsize(1000, binary=False, gnu=True) == "1000B"


def test_decimal_format_without_decimal_places():
    assert filesize.naturalsize(1234567, format="%.0f") == "1 MB"


def test_binary_format_without_decimal_places():
    assert filesize.naturalsize(1024**2, binary=True, format="%.0f") == "1 MiB"


def test_gnu_format_without_decimal_places():
    assert filesize.naturalsize(1024**2, gnu=True, format="%.0f") == "1M"


def test_custom_format_scientific_notation():
    assert filesize.naturalsize(1000000, format="%.2e") == "1.00e+00 MB"


def test_format_with_literal_text():
    assert filesize.naturalsize(1000, format="size=%.1f") == "size=1.0 kB"


def test_format_with_escaped_percent():
    assert filesize.naturalsize(1000, format="%.1f%%") == "1.0% kB"


def test_large_values_with_custom_format():
    assert filesize.naturalsize(10**30, format="%.2f") == "1.00 QB"
    assert filesize.naturalsize(2**100, binary=True, format="%.2f") == "1.00 QiB"
