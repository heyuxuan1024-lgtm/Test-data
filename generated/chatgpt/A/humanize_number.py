
import math
import pytest

from humanize.number import (
    _format_not_finite,
    ordinal,
    intcomma,
    intword,
    apnumber,
    fractional,
    scientific,
    clamp,
    metric,
    powers,
    human_powers,
    _SUPERSCRIPT_MAP,
    _ORDINAL_SUFFIXES,
    _APNUMBER_WORDS,
)


@pytest.mark.parametrize(
    "value, expected",
    [
        (1, "1st"),
        (2, "2nd"),
        (3, "3rd"),
        (4, "4th"),
        (5, "5th"),
        (9, "9th"),
        (10, "10th"),
        (11, "11th"),
        (12, "12th"),
        (13, "13th"),
        (14, "14th"),
        (20, "20th"),
        (21, "21st"),
        (22, "22nd"),
        (23, "23rd"),
        (24, "24th"),
        (100, "100th"),
        (101, "101st"),
        (102, "102nd"),
        (103, "103rd"),
        (111, "111th"),
        (112, "112th"),
        (113, "113th"),
        (121, "121st"),
        (1002, "1002nd"),
    ],
)
def test_ordinal(value, expected):
    assert ordinal(value) == expected


@pytest.mark.parametrize(
    "value",
    [-1, -2, -3, -4, -11, -12, -13, -21, -22, -23, -101],
)
def test_ordinal_negative(value):
    result = ordinal(value)
    assert result.startswith(str(value))


def test_ordinal_float():
    assert ordinal(1.9) == "1st"
    assert ordinal(2.9) == "2nd"
    assert ordinal(-3.9) == "-3rd"


def test_ordinal_string():
    assert ordinal("1") == "1st"
    assert ordinal("12") == "12th"
    assert ordinal("103") == "103rd"


def test_ordinal_invalid_string():
    assert ordinal("something else") == "something else"


def test_ordinal_none():
    assert ordinal(None) == "None"


def test_ordinal_list():
    assert ordinal([1, 2, 3]) == "[1, 2, 3]"


def test_ordinal_boolean():
    assert ordinal(True) == "1st"
    assert ordinal(False) == "0th"


def test_ordinal_gender():
    assert ordinal(1, gender="male") == "1st"
    assert ordinal(1, gender="female") == "1st"
    assert ordinal(2, gender="female") == "2nd"
    assert ordinal(3, gender="other") == "3rd"


@pytest.mark.parametrize(
    "value, expected",
    [
        (float("nan"), "NaN"),
        (float("inf"), "+Inf"),
        (float("-inf"), "-Inf"),
    ],
)
def test_ordinal_non_finite(value, expected):
    assert ordinal(value) == expected


def test_ordinal_large_number():
    assert ordinal(10**100).endswith("th")


def test_ordinal_invalid_object():
    value = object()
    assert ordinal(value) == str(value)


def test_ordinal_suffix_constants():
    assert len(_ORDINAL_SUFFIXES) == 10
    assert _ORDINAL_SUFFIXES[0] == "th"
    assert _ORDINAL_SUFFIXES[1] == "st"
    assert _ORDINAL_SUFFIXES[2] == "nd"
    assert _ORDINAL_SUFFIXES[3] == "rd"


def test_format_not_finite():
    assert _format_not_finite(float("nan")) == "NaN"
    assert _format_not_finite(float("inf")) == "+Inf"
    assert _format_not_finite(float("-inf")) == "-Inf"
    assert _format_not_finite(1.0) == ""


@pytest.mark.parametrize(
    "value, expected",
    [
        (0, "0"),
        (1, "1"),
        (999, "999"),
        (1000, "1,000"),
        (3000, "3,000"),
        (45000, "45,000"),
        (1000000, "1,000,000"),
        (123456789, "123,456,789"),
        (-1000, "-1,000"),
        (-1234567, "-1,234,567"),
    ],
)
def test_intcomma(value, expected):
    assert intcomma(value) == expected


def test_intcomma_string():
    assert intcomma("1000") == "1,000"
    assert intcomma("1234567") == "1,234,567"


def test_intcomma_float():
    assert intcomma(1234567.25) == "1,234,567.25"
    assert intcomma(-1234567.25) == "-1,234,567.25"


def test_intcomma_string_float():
    assert intcomma("1234567.25") == "1,234,567.25"


@pytest.mark.parametrize(
    "value, ndigits, expected",
    [
        (1234.5454545, 2, "1,234.55"),
        (14308.40, 1, "14,308.4"),
        ("14308.40", 1, "14,308.4"),
        (1234.5, 0, "1,234"),
        (1234.5678, 3, "1,234.568"),
        (-1234.5678, 2, "-1,234.57"),
    ],
)
def test_intcomma_precision(value, ndigits, expected):
    assert intcomma(value, ndigits) == expected


def test_intcomma_none():
    assert intcomma(None) == "None"


@pytest.mark.parametrize(
    "value",
    [
        "abc",
        "",
        "not a number",
        [],
        {},
        object(),
    ],
)
def test_intcomma_invalid_values(value):
    assert intcomma(value) == str(value)


def test_intcomma_non_finite():
    assert intcomma(float("nan")) == "NaN"
    assert intcomma(float("inf")) == "+Inf"
    assert intcomma(float("-inf")) == "-Inf"


def test_intcomma_non_finite_strings():
    assert intcomma("nan") == "NaN"
    assert intcomma("inf") == "+Inf"
    assert intcomma("-inf") == "-Inf"


def test_intcomma_integer_string_with_whitespace():
    assert intcomma(" 1000 ") == " 1000 "


def test_intcomma_existing_commas():
    assert intcomma("1,000,000") == "1000000"


def test_intcomma_boolean():
    assert intcomma(True) == "1"
    assert intcomma(False) == "0"


def test_intcomma_zero_precision():
    assert intcomma(1234.99, 0) == "1,235"


def test_intcomma_negative_precision():
    with pytest.raises(ValueError):
        intcomma(1234.5, -1)


def test_intcomma_large_integer():
    assert intcomma(10**30) == "1,000,000,000,000,000,000,000,000,000,000"


@pytest.mark.parametrize(
    "value, expected",
    [
        (0, "0"),
        (1, "1"),
        (10, "10"),
        (999, "999"),
        (1000, "1.0 thousand"),
        (12000, "12.0 thousand"),
        (1000000, "1.0 million"),
        (1200000, "1.2 million"),
        (1000000000, "1.0 billion"),
        (1200000000, "1.2 billion"),
        (10**12, "1.0 trillion"),
        (10**15, "1.0 quadrillion"),
        (10**18, "1.0 quintillion"),
        (10**21, "1.0 sextillion"),
        (10**24, "1.0 septillion"),
        (10**27, "1.0 octillion"),
        (10**30, "1.0 nonillion"),
        (10**33, "1.0 decillion"),
        (10**100, "1.0 googol"),
    ],
)
def test_intword(value, expected):
    assert intword(value) == expected


def test_intword_string():
    assert intword("100") == "100"
    assert intword("12400") == "12.4 thousand"
    assert intword("1000000") == "1.0 million"


def test_intword_custom_format():
    assert intword("1234000", "%0.3f") == "1.234 million"
    assert intword(1200000, "%.2f") == "1.20 million"
    assert intword(1200000, "%.0f") == "1 million"


def test_intword_negative():
    assert intword(-100) == "-100"
    assert intword(-1000) == "-1.0 thousand"
    assert intword(-1200000) == "-1.2 million"


def test_intword_rounding_to_next_suffix():
    assert intword(999999) == "1.0 million"
    assert intword(999999999) == "1.0 billion"
    assert intword(999999999999) == "1.0 trillion"


def test_intword_invalid_values():
    assert intword(None) == "None"
    assert intword("abc") == "abc"
    assert intword([]) == "[]"


def test_intword_non_finite():
    assert intword(float("nan")) == "NaN"
    assert intword(float("inf")) == "+Inf"
    assert intword(float("-inf")) == "-Inf"


def test_intword_float():
    assert intword(1500.9) == "1.5 thousand"
    assert intword(-1500.9) == "-1.5 thousand"


def test_intword_boolean():
    assert intword(True) == "1"
    assert intword(False) == "0"


def test_intword_suffix_constants():
    assert len(powers) == 12
    assert len(human_powers) == 12
    assert powers == sorted(powers)
    assert human_powers[-1] == ("googol", "googol")


def test_intword_format_error():
    with pytest.raises((TypeError, ValueError)):
        intword(1000000, "invalid")


def test_intword_large_value():
    assert intword(10**101) == "10.0 googol"


@pytest.mark.parametrize(
    "value, expected",
    [
        (0, "zero"),
        (1, "one"),
        (2, "two"),
        (3, "three"),
        (4, "four"),
        (5, "five"),
        (6, "six"),
        (7, "seven"),
        (8, "eight"),
        (9, "nine"),
        (10, "10"),
        (11, "11"),
        (-1, "-1"),
        (100, "100"),
    ],
)
def test_apnumber(value, expected):
    assert apnumber(value) == expected


def test_apnumber_string():
    assert apnumber("7") == "seven"
    assert apnumber("10") == "10"


def test_apnumber_invalid_values():
    assert apnumber("foo") == "foo"
    assert apnumber(None) == "None"
    assert apnumber([]) == "[]"


def test_apnumber_non_finite():
    assert apnumber(float("nan")) == "NaN"
    assert apnumber(float("inf")) == "+Inf"
    assert apnumber(float("-inf")) == "-Inf"


def test_apnumber_float():
    assert apnumber(5.9) == "five"
    assert apnumber(9.9) == "nine"
    assert apnumber(10.9) == "10"


def test_apnumber_boolean():
    assert apnumber(True) == "one"
    assert apnumber(False) == "zero"


def test_apnumber_words_constant():
    assert _APNUMBER_WORDS == (
        "zero",
        "one",
        "two",
        "three",
        "four",
        "five",
        "six",
        "seven",
        "eight",
        "nine",
    )


@pytest.mark.parametrize(
    "value, expected",
    [
        (0, "0/1"),
        (0.3, "3/10"),
        (0.5, "1/2"),
        (0.25, "1/4"),
        (0.75, "3/4"),
        (1, "1"),
        (1.0, "1"),
        (1.3, "1 3/10"),
        (2.5, "2 1/2"),
        (3.75, "3 3/4"),
        (-0.5, "-1/2"),
        (-1.3, "-1 3/10"),
        (-2.5, "-2 1/2"),
        (-3.75, "-3 3/4"),
    ],
)
def test_fractional(value, expected):
    assert fractional(value) == expected


def test_fractional_string():
    assert fractional("0.5") == "1/2"
    assert fractional("1.25") == "1 1/4"


def test_fractional_integer_string():
    assert fractional("5") == "5"
    assert fractional("-5") == "-5"


def test_fractional_invalid_values():
    assert fractional("ten") == "ten"
    assert fractional(None) == "None"
    assert fractional([]) == "[]"


def test_fractional_non_finite():
    assert fractional(float("nan")) == "NaN"
    assert fractional(float("inf")) == "+Inf"
    assert fractional(float("-inf")) == "-Inf"


def test_fractional_repeating_decimal():
    assert fractional(1 / 3) == "1/3"
    assert fractional(2 / 3) == "2/3"


def test_fractional_limited_denominator():
    result = fractional(0.123456789)
    assert result == "10/81"


def test_fractional_negative_integer():
    assert fractional(-1.0) == "-1"
    assert fractional(-10.0) == "-10"


def test_fractional_small_negative():
    assert fractional(-0.3) == "-3/10"


@pytest.mark.parametrize(
    "value, expected",
    [
        (0, "0.00 x 10⁰"),
        (1, "1.00 x 10⁰"),
        (10, "1.00 x 10¹"),
        (100, "1.00 x 10²"),
        (500, "5.00 x 10²"),
        (1000, "1.00 x 10³"),
        (-1000, "-1.00 x 10³"),
        (0.3, "3.00 x 10⁻¹"),
        (0.01, "1.00 x 10⁻²"),
        (0.001, "1.00 x 10⁻³"),
        (123456, "1.23 x 10⁵"),
        ("99", "9.90 x 10¹"),
    ],
)
def test_scientific(value, expected):
    assert scientific(value) == expected


def test_scientific_precision():
    assert scientific(1000, 1) == "1.0 x 10³"
    assert scientific(1000, 3) == "1.000 x 10³"
    assert scientific(12345, 4) == "1.2345 x 10⁴"


def test_scientific_negative_exponent():
    assert scientific(0.0001) == "1.00 x 10⁻⁴"


def test_scientific_invalid_values():
    assert scientific("foo") == "foo"
    assert scientific(None) == "None"


def test_scientific_non_finite():
    assert scientific(float("nan")) == "NaN"
    assert scientific(float("inf")) == "+Inf"
    assert scientific(float("-inf")) == "-Inf"


def test_scientific_boolean():
    assert scientific(True) == "1.00 x 10⁰"
    assert scientific(False) == "0.00 x 10⁰"


def test_scientific_negative_precision():
    with pytest.raises(ValueError):
        scientific(1000, -1)


def test_scientific_invalid_precision():
    with pytest.raises((TypeError, ValueError)):
        scientific(1000, "invalid")


def test_scientific_superscript_map():
    assert _SUPERSCRIPT_MAP["0"] == "⁰"
    assert _SUPERSCRIPT_MAP["1"] == "¹"
    assert _SUPERSCRIPT_MAP["-"] == "⁻"
    assert len(_SUPERSCRIPT_MAP) == 11


@pytest.mark.parametrize(
    "value, expected",
    [
        (123.456, "123.456"),
        (0, "0"),
        (-10, "-10"),
        (1.5, "1.5"),
    ],
)
def test_clamp_without_limits(value, expected):
    assert clamp(value) == expected


def test_clamp_floor():
    assert clamp(0.0001, floor=0.01) == "<0.01"
    assert clamp(-10, floor=0) == "<0"


def test_clamp_ceil():
    assert clamp(1.5, ceil=1) == ">1"
    assert clamp(100, ceil=99) == ">99"


def test_clamp_within_limits():
    assert clamp(5, floor=1, ceil=10) == "5"
    assert clamp(1, floor=1, ceil=10) == "1"
    assert clamp(10, floor=1, ceil=10) == "10"


def test_clamp_floor_token():
    assert clamp(1, floor=10, floor_token="under ") == "under 10"


def test_clamp_ceil_token():
    assert clamp(20, ceil=10, ceil_token="over ") == "over 10"


def test_clamp_percentage_format():
    assert clamp(0.99, format="{:.0%}", ceil=0.99) == "99%"
    assert clamp(0.999, format="{:.0%}", ceil=0.99) == ">99%"


def test_clamp_callable_format():
    assert clamp(1234, format=lambda value: f"{value:,}") == "1,234"


def test_clamp_callable_with_floor():
    assert clamp(1, format=str, floor=10, floor_token="under ") == "under 10"


def test_clamp_callable_with_ceil():
    assert clamp(20, format=lambda value: str(value * 2), ceil=10) == ">20"


def test_clamp_intword_callable():
    assert clamp(1, format=lambda value: "small" if value < 10 else "large") == "small"


def test_clamp_none():
    assert clamp(None) is None


@pytest.mark.parametrize(
    "value, expected",
    [
        (float("nan"), "NaN"),
        (float("inf"), "+Inf"),
        (float("-inf"), "-Inf"),
    ],
)
def test_clamp_non_finite(value, expected):
    assert clamp(value) == expected


def test_clamp_invalid_format():
    with pytest.raises(ValueError, match="Invalid format"):
        clamp(10, format=123)


def test_clamp_invalid_callable_result():
    assert clamp(10, format=lambda value: value) == 10


def test_clamp_format_error():
    with pytest.raises((ValueError, IndexError)):
        clamp(10, format="{invalid}")


def test_clamp_floor_precedence():
    assert clamp(0, floor=5, ceil=10) == "<5"


def test_clamp_floor_and_ceil():
    assert clamp(20, floor=5, ceil=10) == ">10"


@pytest.mark.parametrize(
    "value, unit, precision, expected",
    [
        (1500, "V", 3, "1.50 kV"),
        (2e8, "W", 3, "200 MW"),
        (220e-6, "F", 3, "220 μF"),
        (1e-14, "", 4, "10.00 f"),
        (0, "", 3, "0.00"),
        (1, "", 3, "1.00"),
        (1000, "", 3, "1.00 k"),
        (1000000, "", 3, "1.00 M"),
        (-1000, "V", 3, "-1.00 kV"),
        (123000, "", 3, "123 k"),
    ],
)
def test_metric(value, unit, precision, expected):
    assert metric(value, unit, precision) == expected


def test_metric_common_prefixes():
    assert metric(1e3) == "1.00 k"
    assert metric(1e6) == "1.00 M"
    assert metric(1e9) == "1.00 G"
    assert metric(1e12) == "1.00 T"
    assert metric(1e15) == "1.00 P"
    assert metric(1e18) == "1.00 E"
    assert metric(1e21) == "1.00 Z"
    assert metric(1e24) == "1.00 Y"
    assert metric(1e27) == "1.00 R"
    assert metric(1e30) == "1.00 Q"


def test_metric_small_prefixes():
    assert metric(1e-3) == "1.00 m"
    assert metric(1e-6) == "1.00 μ"
    assert metric(1e-9) == "1.00 n"
    assert metric(1e-12) == "1.00 p"
    assert metric(1e-15) == "1.00 f"
    assert metric(1e-18) == "1.00 a"
    assert metric(1e-21) == "1.00 z"
    assert metric(1e-24) == "1.00 y"
    assert metric(1e-27) == "1.00 r"
    assert metric(1e-30) == "1.00 q"


def test_metric_zero():
    assert metric(0) == "0.00"
    assert metric(0, "V") == "0.00 V"


def test_metric_non_finite():
    assert metric(float("nan")) == "NaN"
    assert metric(float("inf")) == "+Inf"
    assert metric(float("-inf")) == "-Inf"


def test_metric_extremely_large():
    assert metric(1e40) == "1.00 x 10⁴⁰"
    assert metric(1e40, "V") == "1.00 x 10⁴⁰V"


def test_metric_extremely_small():
    assert metric(1e-31) == "1.00 x 10⁻³¹"
    assert metric(1e-31, "F") == "1.00 x 10⁻³¹F"


def test_metric_precision():
    assert metric(1500, "V", precision=2) == "1.5 kV"
    assert metric(1500, "V", precision=4) == "1.500 kV"
    assert metric(1500, "V", precision=5) == "1.5000 kV"


def test_metric_rounding_bucket_transition():
    assert metric(999.9, precision=3) == "1.00 k"
    assert metric(999999.9, precision=3) == "1.00 M"
    assert metric(999999999.9, precision=3) == "1.00 G"


def test_metric_unit_spacing():
    assert metric(1000, "V") == "1.00 kV"
    assert metric(1000, "°") == "1.00k°"
    assert metric(1000, "′") == "1.00k′"
    assert metric(1000, "″") == "1.00k″"


def test_metric_no_unit():
    assert metric(1000) == "1.00 k"
    assert metric(0.001) == "1.00 m"


def test_metric_negative_values():
    assert metric(-1500, "V") == "-1.50 kV"
    assert metric(-0.001) == "-1.00 m"


def test_metric_fractional_values():
    assert metric(0.5) == "500 m"
    assert metric(0.0005) == "500 μ"


def test_metric_large_prefix_boundary():
    assert metric(1e33) == "1.00 x 10³³"
    assert metric(1e32) == "100 Q"


def test_metric_small_prefix_boundary():
    assert metric(1e-30) == "1.00 q"
    assert metric(1e-31) == "1.00 x 10⁻³¹"


def test_metric_invalid_value():
    with pytest.raises(TypeError):
        metric("invalid")


def test_metric_invalid_unit():
    with pytest.raises(TypeError):
        metric(1000, unit=None)


def test_metric_invalid_precision():
    with pytest.raises((TypeError, ValueError)):
        metric(1000, precision="invalid")


def test_metric_zero_precision():
    assert metric(1234, precision=0) == "1 k"


def test_metric_negative_precision():
    with pytest.raises(ValueError):
        metric(1000, precision=-1)


def test_metric_rounding_with_negative_value():
    assert metric(-999.9, precision=3) == "-1.00 k"


def test_metric_small_value_with_unit():
    assert metric(0.000001, "F") == "1.00 μF"


def test_metric_very_small_negative_value():
    assert metric(-1e-40, "V") == "-1.00 x 10⁻⁴⁰V"


def test_metric_exponent_zero():
    assert metric(1, precision=1) == "1"


def test_metric_exponent_positive():
    assert metric(100, precision=1) == "100"


def test_metric_exponent_negative():
    assert metric(0.1, precision=1) == "100 m"


def test_metric_prefix_with_unit():
    assert metric(1e6, "W") == "1.00 MW"


def test_metric_rounding_preserves_sign():
    assert metric(-999.9) == "-1.00 k"


def test_metric_precision_large():
    assert metric(1234.567, precision=6) == "1.23457 k"


def test_metric_unit_only():
    assert metric(1, "m") == "1.00 m"


def test_metric_special_unit_spacing():
    for unit in ("°", "′", "″"):
        assert metric(1000, unit).startswith("1.00k")
