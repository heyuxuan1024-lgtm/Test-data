
import math

import pytest
from humanize import number


def test_module_constants():
    assert number.__lazy_modules__ == {"bisect"}
    assert number.TYPE_CHECKING is False
    assert number.powers == [
        10**3, 10**6, 10**9, 10**12, 10**15, 10**18,
        10**21, 10**24, 10**27, 10**30, 10**33, 10**100,
    ]
    assert len(number.human_powers) == len(number.powers)


@pytest.mark.parametrize(
    "value, expected",
    [
        (0, "0th"),
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
        (101, "101st"),
        (102, "102nd"),
        (103, "103rd"),
        (111, "111th"),
        (112, "112th"),
        (113, "113th"),
        (121, "121st"),
        (1002, "1002nd"),
        (-1, "-1st"),
        (-2, "-2nd"),
        (-3, "-3rd"),
        (-4, "-4th"),
        (-11, "-11th"),
        (-21, "-21st"),
    ],
)
def test_ordinal(value, expected):
    assert number.ordinal(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        ("1", "1st"),
        ("2", "2nd"),
        ("3", "3rd"),
        ("12", "12th"),
        ("101", "101st"),
        ("1.9", "1.9"),
        ("something else", "something else"),
        (None, "None"),
        ([1, 2, 3], "[1, 2, 3]"),
        ({}, "{}"),
        (1.9, "1st"),
        (-1.9, "-1st"),
        (True, "1st"),
        (False, "0th"),
    ],
)
def test_ordinal_conversions_and_fallbacks(value, expected):
    assert number.ordinal(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (float("nan"), "NaN"),
        (float("inf"), "+Inf"),
        (float("-inf"), "-Inf"),
        ("nan", "NaN"),
        ("inf", "+Inf"),
        ("-inf", "-Inf"),
    ],
)
def test_ordinal_non_finite(value, expected):
    assert number.ordinal(value) == expected


def test_ordinal_gender_argument():
    assert number.ordinal(1, gender="male") == "1st"
    assert number.ordinal(1, gender="female") == "1st"
    assert number.ordinal(2, gender="female") == "2nd"
    assert number.ordinal(3, gender="other") == "3rd"


@pytest.mark.parametrize(
    "value, expected",
    [
        (0, "0"),
        (1, "1"),
        (10, "10"),
        (100, "100"),
        (999, "999"),
        (1000, "1,000"),
        (1234, "1,234"),
        (1000000, "1,000,000"),
        (-1234567, "-1,234,567"),
        (1234567.25, "1,234,567.25"),
        (1234.5, "1,234.5"),
        ("1000", "1,000"),
        ("1000000", "1,000,000"),
        ("1234.5", "1,234.5"),
        ("1,234.5", "1,234.5"),
        (None, "None"),
        ("not a number", "not a number"),
        ([1, 2], "[1, 2]"),
    ],
)
def test_intcomma(value, expected):
    assert number.intcomma(value) == expected


@pytest.mark.parametrize(
    "value, ndigits, expected",
    [
        (1234.5454545, 2, "1,234.55"),
        (14308.40, 1, "14,308.4"),
        ("14308.40", 1, "14,308.4"),
        (1234.5, 0, "1,234"),
        (1234.567, 3, "1,234.567"),
        (-1234.567, 2, "-1,234.57"),
        (1000, 2, "1,000.00"),
        ("1000.5", 2, "1,000.50"),
    ],
)
def test_intcomma_precision(value, ndigits, expected):
    assert number.intcomma(value, ndigits) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (float("nan"), "NaN"),
        (float("inf"), "+Inf"),
        (float("-inf"), "-Inf"),
        ("nan", "NaN"),
        ("inf", "+Inf"),
        ("-inf", "-Inf"),
    ],
)
def test_intcomma_non_finite(value, expected):
    assert number.intcomma(value) == expected


def test_intcomma_locale_separators(monkeypatch):
    monkeypatch.setattr(number, "thousands_separator", lambda: ".")
    monkeypatch.setattr(number, "decimal_separator", lambda: ",")
    assert number.intcomma(1234567.89) == "1.234.567,89"
    assert number.intcomma("1.234.567,89") == "1.234.567,89"
    assert number.intcomma("1234,5", 2) == "1.234,50"


def test_intcomma_locale_input_normalization(monkeypatch):
    monkeypatch.setattr(number, "thousands_separator", lambda: "_")
    monkeypatch.setattr(number, "decimal_separator", lambda: ",")
    assert number.intcomma("1_234_567,89") == "1_234_567,89"
    assert number.intcomma("1_234_567,89", 1) == "1_234_567,9"


def test_intcomma_invalid_string_fallback():
    assert number.intcomma("abc") == "abc"
    assert number.intcomma("12x34") == "12x34"
    assert number.intcomma("") == ""


def test_intcomma_invalid_non_string_fallback():
    assert number.intcomma(None) == "None"
    assert number.intcomma(object()).startswith("<object object at ")


def test_intcomma_invalid_ndigits():
    with pytest.raises((ValueError, TypeError)):
        number.intcomma(1234, -1)


@pytest.mark.parametrize(
    "value, expected",
    [
        (0, "0"),
        (1, "1"),
        (999, "999"),
        (1000, "1.0 thousand"),
        (12000, "12.0 thousand"),
        (1000000, "1.0 million"),
        (1200000, "1.2 million"),
        (1200000000, "1.2 billion"),
        (-1000000, "-1.0 million"),
        (-1200000000, "-1.2 billion"),
        ("100", "100"),
        ("12400", "12.4 thousand"),
        ("1000000", "1.0 million"),
        (None, "None"),
        ("not numeric", "not numeric"),
    ],
)
def test_intword(value, expected):
    assert number.intword(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (float("nan"), "NaN"),
        (float("inf"), "+Inf"),
        (float("-inf"), "-Inf"),
        ("nan", "NaN"),
        ("inf", "+Inf"),
        ("-inf", "-Inf"),
    ],
)
def test_intword_non_finite(value, expected):
    assert number.intword(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (10**3, "1.0 thousand"),
        (10**6, "1.0 million"),
        (10**9, "1.0 billion"),
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
def test_intword_all_units(value, expected):
    assert number.intword(value) == expected


def test_intword_above_googol():
    assert number.intword(10**101) == "10.0 googol"


def test_intword_rounding_to_next_unit():
    assert number.intword(999999, format="%.1f") == "1.0 million"
    assert number.intword(999499, format="%.1f") == "999.5 thousand"
    assert number.intword(999999999, format="%.1f") == "1.0 billion"


def test_intword_custom_format():
    assert number.intword(1234000, format="%0.3f") == "1.234 million"
    assert number.intword(1234567, format="%.2f") == "1.23 million"
    assert number.intword(1234567, format="%.0f") == "1 million"


def test_intword_negative_custom_format():
    assert number.intword(-1234000, format="%.3f") == "-1.234 million"


def test_intword_non_integer_numeric_values():
    assert number.intword(1234567.9) == "1.2 million"
    assert number.intword(-1234567.9) == "-1.2 million"
    assert number.intword(999.9) == "999"


def test_intword_invalid_format():
    with pytest.raises((TypeError, ValueError)):
        number.intword(1000000, format="%")
    with pytest.raises((TypeError, ValueError)):
        number.intword(1000000, format="invalid")


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
        (-9, "-9"),
        (1.9, "1"),
        ("7", "seven"),
        ("7.9", "7.9"),
        ("foo", "foo"),
        (None, "None"),
    ],
)
def test_apnumber(value, expected):
    assert number.apnumber(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (float("nan"), "NaN"),
        (float("inf"), "+Inf"),
        (float("-inf"), "-Inf"),
        ("nan", "NaN"),
        ("inf", "+Inf"),
        ("-inf", "-Inf"),
    ],
)
def test_apnumber_non_finite(value, expected):
    assert number.apnumber(value) == expected


def test_apnumber_translation(monkeypatch):
    monkeypatch.setattr(number, "_", lambda value: f"translated-{value}")
    assert number.apnumber(0) == "translated-zero"
    assert number.apnumber(5) == "translated-five"
    assert number.apnumber(10) == "10"


@pytest.mark.parametrize(
    "value, expected",
    [
        (0, "0"),
        (1, "1"),
        (2, "2"),
        (0.3, "3/10"),
        (1.3, "1 3/10"),
        (0.5, "1/2"),
        (1.5, "1 1/2"),
        (2.25, "2 1/4"),
        (0.125, "1/8"),
        (1 / 3, "1/3"),
        (2 / 3, "2/3"),
        (-0.3, "-3/10"),
        (-1.3, "-1 3/10"),
        (-1.5, "-1 1/2"),
        (1.0000, "1"),
        ("ten", "ten"),
        (None, "None"),
    ],
)
def test_fractional(value, expected):
    assert number.fractional(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (float("nan"), "NaN"),
        (float("inf"), "+Inf"),
        (float("-inf"), "-Inf"),
        ("nan", "NaN"),
        ("inf", "+Inf"),
        ("-inf", "-Inf"),
    ],
)
def test_fractional_non_finite(value, expected):
    assert number.fractional(value) == expected


def test_fractional_numeric_strings():
    assert number.fractional("0.3") == "3/10"
    assert number.fractional("1.25") == "1 1/4"
    assert number.fractional("-1.25") == "-1 1/4"


def test_fractional_approximates_to_limited_denominator():
    assert number.fractional(0.3333333333333333) == "1/3"
    assert number.fractional(0.14285714285714285) == "1/7"


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
        (0.03, "3.00 x 10⁻²"),
        (0.003, "3.00 x 10⁻³"),
        (99, "9.90 x 10¹"),
        ("99", "9.90 x 10¹"),
        ("foo", "foo"),
        (None, "None"),
    ],
)
def test_scientific(value, expected):
    assert number.scientific(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (float("nan"), "NaN"),
        (float("inf"), "+Inf"),
        (float("-inf"), "-Inf"),
        ("nan", "NaN"),
        ("inf", "+Inf"),
        ("-inf", "-Inf"),
    ],
)
def test_scientific_non_finite(value, expected):
    assert number.scientific(value) == expected


@pytest.mark.parametrize(
    "precision, expected",
    [
        (0, "5 x 10²"),
        (1, "5.0 x 10²"),
        (2, "5.00 x 10²"),
        (3, "5.000 x 10²"),
        (4, "5.0000 x 10²"),
    ],
)
def test_scientific_precision(precision, expected):
    assert number.scientific(500, precision) == expected


def test_scientific_normalizes_exponent():
    assert number.scientific(1) == "1.00 x 10⁰"
    assert number.scientific(1000) == "1.00 x 10³"
    assert number.scientific(0.001) == "1.00 x 10⁻³"


def test_scientific_numeric_strings():
    assert number.scientific("1000") == "1.00 x 10³"
    assert number.scientific("0.3") == "3.00 x 10⁻¹"


@pytest.mark.parametrize("precision", [-1, -2])
def test_scientific_negative_precision(precision):
    with pytest.raises(ValueError):
        number.scientific(1000, precision)


def test_scientific_non_integer_precision():
    assert number.scientific(1000, 2.9) == "1.00 x 10³"


@pytest.mark.parametrize(
    "value, expected",
    [
        (123.456, "123.456"),
        (0, "0"),
        (1, "1"),
        (-1, "-1"),
        (0.0001, "0.0001"),
    ],
)
def test_clamp_without_limits(value, expected):
    assert number.clamp(value) == expected


def test_clamp_floor():
    assert number.clamp(0.0001, floor=0.01) == "<0.01"
    assert number.clamp(-10, floor=0) == "<0"
    assert number.clamp(0.01, floor=0.01) == "0.01"


def test_clamp_ceil():
    assert number.clamp(1.0, ceil=0.99) == ">0.99"
    assert number.clamp(10, ceil=5) == ">5"
    assert number.clamp(5, ceil=5) == "5"


def test_clamp_floor_and_ceil():
    assert number.clamp(-1, floor=0, ceil=10) == "<0"
    assert number.clamp(11, floor=0, ceil=10) == ">10"
    assert number.clamp(5, floor=0, ceil=10) == "5"


def test_clamp_custom_tokens():
    assert number.clamp(0.0001, floor=0.01, floor_token="under ") == "under 0.01"
    assert number.clamp(1, ceil=0.99, ceil_token="over ") == "over 0.99"
    assert number.clamp(-1, floor=0, floor_token="LOW:") == "LOW:0"


def test_clamp_custom_format_string():
    assert number.clamp(0.99, format="{:.0%}", ceil=0.99) == "99%"
    assert number.clamp(0.999, format="{:.0%}", ceil=0.99) == ">99%"
    assert number.clamp(1.23456, format="{:.2f}") == "1.23"
    assert number.clamp(1234, format="{:,.1f}") == "1,234.0"


def test_clamp_callable_format():
    assert number.clamp(1234, format=lambda value: str(int(value))) == "1234"
    assert number.clamp(0, floor=10, format=lambda value: f"{value:.1f}") == "<10.0"
    assert number.clamp(20, ceil=10, format=lambda value: f"{value:.1f}") == ">10.0"


def test_clamp_intword_callable():
    assert number.clamp(1, format=number.intword, floor=10**6) == "<1.0 million"


def test_clamp_none():
    assert number.clamp(None) is None


@pytest.mark.parametrize(
    "value, expected",
    [
        (float("nan"), "NaN"),
        (float("inf"), "+Inf"),
        (float("-inf"), "-Inf"),
    ],
)
def test_clamp_non_finite(value, expected):
    assert number.clamp(value) == expected


def test_clamp_non_finite_ignores_limits_and_format():
    assert number.clamp(float("inf"), floor=0, ceil=10) == "+Inf"
    assert number.clamp(float("-inf"), floor=0, ceil=10) == "-Inf"
    assert number.clamp(float("nan"), format=object()) == "NaN"


def test_clamp_invalid_format():
    with pytest.raises(ValueError, match="Invalid format"):
        number.clamp(1, format=object())
    with pytest.raises(ValueError, match="Invalid format"):
        number.clamp(1, format=None)


def test_clamp_invalid_format_after_clamping():
    with pytest.raises(ValueError, match="Invalid format"):
        number.clamp(-1, floor=0, format=object())


def test_clamp_invalid_format_string():
    with pytest.raises((ValueError, IndexError, KeyError)):
        number.clamp(1, format="{")
    with pytest.raises((ValueError, IndexError, KeyError)):
        number.clamp(1, format="{missing}")


@pytest.mark.parametrize(
    "value, unit, precision, expected",
    [
        (0, "", 3, "0.00"),
        (1, "", 3, "1.00"),
        (1000, "V", 3, "1.00 kV"),
        (1500, "V", 3, "1.50 kV"),
        (2e8, "W", 3, "200 MW"),
        (220e-6, "F", 3, "220 μF"),
        (1e-14, "", 4, "10.00 f"),
        (123000, "", 3, "123 k"),
        (1230000, "", 3, "1.23 M"),
        (-1500, "V", 3, "-1.50 kV"),
    ],
)
def test_metric(value, unit, precision, expected):
    assert number.metric(value, unit, precision) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (float("nan"), "NaN"),
        (float("inf"), "+Inf"),
        (float("-inf"), "-Inf"),
    ],
)
def test_metric_non_finite(value, expected):
    assert number.metric(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (1e3, "1.00 k"),
        (1e6, "1.00 M"),
        (1e9, "1.00 G"),
        (1e12, "1.00 T"),
        (1e15, "1.00 P"),
        (1e18, "1.00 E"),
        (1e21, "1.00 Z"),
        (1e24, "1.00 Y"),
        (1e27, "1.00 R"),
        (1e30, "1.00 Q"),
    ],
)
def test_metric_positive_prefixes(value, expected):
    assert number.metric(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (1e-3, "1.00 m"),
        (1e-6, "1.00 μ"),
        (1e-9, "1.00 n"),
        (1e-12, "1.00 p"),
        (1e-15, "1.00 f"),
        (1e-18, "1.00 a"),
        (1e-21, "1.00 z"),
        (1e-24, "1.00 y"),
        (1e-27, "1.00 r"),
        (1e-30, "1.00 q"),
    ],
)
def test_metric_negative_prefixes(value, expected):
    assert number.metric(value) == expected


def test_metric_unit_spacing():
    assert number.metric(1500, "V") == "1.50 kV"
    assert number.metric(1500) == "1.50 k"
    assert number.metric(1500, "°") == "1.50°"
    assert number.metric(1500, "′") == "1.50′"
    assert number.metric(1500, "″") == "1.50″"
    assert number.metric(1500, "m") == "1.50 km"


def test_metric_precision():
    assert number.metric(1500, "V", precision=1) == "2 kV"
    assert number.metric(1500, "V", precision=2) == "1.5 kV"
    assert number.metric(1500, "V", precision=4) == "1.500 kV"


def test_metric_rounding_promotes_prefix():
    assert number.metric(999999, precision=3) == "1.00 M"
    assert number.metric(999499, precision=3) == "999 k"
    assert number.metric(999950, precision=3) == "1.00 M"


def test_metric_does_not_promote_at_exponent_thirty_or_above():
    assert number.metric(9.999e32) == "1000 Q"


def test_metric_scientific_fallback_for_large_values():
    assert number.metric(1e33) == "1.00 x 10³³"
    assert number.metric(1e40) == "1.00 x 10⁴⁰"
    assert number.metric(1e40, "V") == "1.00 x 10⁴⁰V"


def test_metric_scientific_fallback_for_small_values():
    assert number.metric(1e-31) == "1.00 x 10⁻³¹"
    assert number.metric(1e-40, "F") == "1.00 x 10⁻⁴⁰F"


def test_metric_zero_with_unit():
    assert number.metric(0, "V") == "0.00 V"


def test_metric_negative_values():
    assert number.metric(-220e-6, "F") == "-220 μF"
    assert number.metric(-1e-6) == "-1.00 μ"


def test_metric_integer_input():
    assert number.metric(1500, "V") == "1.50 kV"


def test_format_not_finite_helper():
    assert number._format_not_finite(float("nan")) == "NaN"
    assert number._format_not_finite(float("inf")) == "+Inf"
    assert number._format_not_finite(float("-inf")) == "-Inf"
    assert number._format_not_finite(1.0) == ""
    assert number._format_not_finite(0.0) == ""
