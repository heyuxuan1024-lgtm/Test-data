import math
from fractions import Fraction

import pytest

from humanize import number


@pytest.fixture
def european_separators(monkeypatch):
    monkeypatch.setattr(number, "thousands_separator", lambda: ".")
    monkeypatch.setattr(number, "decimal_separator", lambda: ",")


def test_module_constants():
    assert len(number.powers) == 12
    assert len(number.human_powers) == 12
    assert number.powers[0] == 1000
    assert number.powers[-2] == 10**33
    assert number.powers[-1] == 10**100
    assert number.powers == sorted(number.powers)
    names = [
        "thousand",
        "million",
        "billion",
        "trillion",
        "quadrillion",
        "quintillion",
        "sextillion",
        "septillion",
        "octillion",
        "nonillion",
        "decillion",
        "googol",
    ]
    for entry, name in zip(number.human_powers, names):
        assert list(entry) == [name, name]
    assert len(number._ORDINAL_SUFFIXES) == 10
    assert len(number._APNUMBER_WORDS) == 10
    assert "-0123456789".translate(number._SUPERSCRIPT_TRANS) == "⁻⁰¹²³⁴⁵⁶⁷⁸⁹"


def test_format_not_finite():
    assert number._format_not_finite(float("nan")) == "NaN"
    assert number._format_not_finite(float("-inf")) == "-Inf"
    assert number._format_not_finite(float("inf")) == "+Inf"
    assert number._format_not_finite(1.5) == ""
    assert number._format_not_finite(0) == ""


@pytest.mark.parametrize(
    "value, expected",
    [
        (0, "0th"),
        (1, "1st"),
        (2, "2nd"),
        (3, "3rd"),
        (4, "4th"),
        (9, "9th"),
        (10, "10th"),
        (11, "11th"),
        (12, "12th"),
        (13, "13th"),
        (14, "14th"),
        (21, "21st"),
        (22, "22nd"),
        (23, "23rd"),
        (101, "101st"),
        (102, "102nd"),
        (103, "103rd"),
        (111, "111th"),
        (112, "112th"),
        (113, "113th"),
        (1002, "1002nd"),
        (1011, "1011th"),
    ],
)
def test_ordinal_integers(value, expected):
    assert number.ordinal(value) == expected


def test_ordinal_coerces_numeric_input():
    assert number.ordinal("3") == "3rd"
    assert number.ordinal(3.7) == "3rd"
    assert number.ordinal("21") == "21st"


@pytest.mark.parametrize(
    "value, expected",
    [
        ("something else", "something else"),
        ([1, 2, 3], "[1, 2, 3]"),
        (None, "None"),
        ("", ""),
        ("3.7", "3.7"),
        ({}, "{}"),
    ],
)
def test_ordinal_non_integer_returns_str(value, expected):
    assert number.ordinal(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (float("nan"), "NaN"),
        (float("inf"), "+Inf"),
        (float("-inf"), "-Inf"),
        ("inf", "+Inf"),
        ("-inf", "-Inf"),
        ("nan", "NaN"),
    ],
)
def test_ordinal_not_finite(value, expected):
    assert number.ordinal(value) == expected


def test_ordinal_gender_context(monkeypatch):
    monkeypatch.setattr(number, "P_", lambda ctx, msg: f"{ctx}|{msg}")
    assert number.ordinal(1) == "11 (male)|st"
    assert number.ordinal(1, "male") == "11 (male)|st"
    assert number.ordinal(2, "female") == "22 (female)|nd"
    assert number.ordinal(1, "other") == "11 (female)|st"
    assert number.ordinal(11) == "110 (male)|th"
    assert number.ordinal(13, "female") == "130 (female)|th"


def test_ordinal_overflow_raises():
    with pytest.raises(OverflowError):
        number.ordinal(10**400)


@pytest.mark.parametrize(
    "value, expected",
    [
        (0, "0"),
        (100, "100"),
        (999, "999"),
        (1000, "1,000"),
        ("1000", "1,000"),
        (1_000_000, "1,000,000"),
        (-1000, "-1,000"),
        ("-1000", "-1,000"),
        (1_234_567.25, "1,234,567.25"),
        (1000.0, "1,000.0"),
        ("1234.5", "1,234.5"),
        ("1,000", "1,000"),
        ("1,234.5", "1,234.5"),
    ],
)
def test_intcomma_values(value, expected):
    assert number.intcomma(value) == expected


@pytest.mark.parametrize(
    "value, ndigits, expected",
    [
        (1234.5454545, 2, "1,234.55"),
        (14308.40, 1, "14,308.4"),
        ("14308.40", 1, "14,308.4"),
        (1000.0, 0, "1,000"),
        ("1000", 2, "1,000.00"),
        (1234567, 0, "1,234,567"),
        (0.5, 3, "0.500"),
    ],
)
def test_intcomma_ndigits(value, ndigits, expected):
    assert number.intcomma(value, ndigits) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (None, "None"),
        ("abc", "abc"),
        ("", ""),
        ([], "[]"),
        ("1e3", "1e3"),
    ],
)
def test_intcomma_invalid_returns_str(value, expected):
    assert number.intcomma(value) == expected


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
def test_intcomma_not_finite(value, expected):
    assert number.intcomma(value) == expected


def test_intcomma_overflow_raises():
    with pytest.raises(OverflowError):
        number.intcomma(10**400)


def test_intcomma_european_separators(european_separators):
    assert number.intcomma(1234567.25) == "1.234.567,25"
    assert number.intcomma(1234567) == "1.234.567"
    assert number.intcomma(1234.5454545, 2) == "1.234,55"
    assert number.intcomma("1.234.567,25") == "1.234.567,25"
    assert number.intcomma("1.234,5") == "1.234,5"
    assert number.intcomma("1.000") == "1.000"
    assert number.intcomma("nan") == "NaN"
    assert number.intcomma("abc") == "abc"


def test_intcomma_space_separator(monkeypatch):
    monkeypatch.setattr(number, "thousands_separator", lambda: " ")
    monkeypatch.setattr(number, "decimal_separator", lambda: ",")
    assert number.intcomma(1234567.25) == "1 234 567,25"
    assert number.intcomma(1234567) == "1 234 567"


def test_intcomma_only_thousands_separator_differs(monkeypatch):
    monkeypatch.setattr(number, "thousands_separator", lambda: "'")
    monkeypatch.setattr(number, "decimal_separator", lambda: ".")
    assert number.intcomma(1234567) == "1'234'567"
    assert number.intcomma(1234.5) == "1'234.5"


@pytest.mark.parametrize(
    "value, expected",
    [
        ("100", "100"),
        ("12400", "12.4 thousand"),
        ("1000000", "1.0 million"),
        (1_200_000_000, "1.2 billion"),
        (8100000000000000000000000000000000, "8.1 decillion"),
        (0, "0"),
        (999, "999"),
        (1000, "1.0 thousand"),
        (1_000_000_000_000, "1.0 trillion"),
        (1_200_000.0, "1.2 million"),
        ("1234567", "1.2 million"),
        (12345678, "12.3 million"),
        (999.9, "999"),
        (10**30, "1.0 nonillion"),
        (10**33, "1.0 decillion"),
        (10**34, "10.0 decillion"),
    ],
)
def test_intword_values(value, expected):
    assert number.intword(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (-999, "-999"),
        (-1000, "-1.0 thousand"),
        (-1_200_000, "-1.2 million"),
        (-999999, "-1.0 million"),
    ],
)
def test_intword_negative(value, expected):
    assert number.intword(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (999_999, "1.0 million"),
        (999_999_999, "1.0 billion"),
        (999_999_999_999, "1.0 trillion"),
        (999_949, "999.9 thousand"),
    ],
)
def test_intword_rounding_steps_up(value, expected):
    assert number.intword(value) == expected


def test_intword_googol():
    assert number.intword(10**100) == "1.0 googol"
    assert number.intword(10**101) == "10.0 googol"
    assert number.intword(10**110) == "10000000000.0 googol"
    assert number.intword(-(10**100)) == "-1.0 googol"


def test_intword_custom_format():
    assert number.intword("1234000", "%0.3f") == "1.234 million"
    assert number.intword(1_500_000, "%.0f") == "2 million"
    assert number.intword(12_345_678, "%.2f") == "12.35 million"


@pytest.mark.parametrize(
    "value, expected",
    [
        (None, "None"),
        ("abc", "abc"),
        ("", ""),
        ([], "[]"),
        ("1e6", "1e6"),
    ],
)
def test_intword_invalid_returns_str(value, expected):
    assert number.intword(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (float("nan"), "NaN"),
        (float("inf"), "+Inf"),
        (float("-inf"), "-Inf"),
    ],
)
def test_intword_not_finite(value, expected):
    assert number.intword(value) == expected


def test_intword_overflow_raises():
    with pytest.raises(OverflowError):
        number.intword(10**400)


def test_intword_decimal_separator(monkeypatch):
    monkeypatch.setattr(number, "decimal_separator", lambda: ",")
    assert number.intword(1_200_000) == "1,2 million"
    assert number.intword(500) == "500"


def test_intword_pluralisation_count(monkeypatch):
    monkeypatch.setattr(
        number, "_ngettext", lambda singular, plural, n: f"{singular}:{n}"
    )
    assert number.intword(1_000_000) == "1.0 million:1"
    assert number.intword(1_500_000) == "1.5 million:2"
    assert number.intword(5_000_000) == "5.0 million:5"
    assert number.intword(999_999) == "1.0 million:1"


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
        (100, "100"),
        (-1, "-1"),
        ("7", "seven"),
        (5.9, "five"),
        (10.5, "10"),
    ],
)
def test_apnumber_values(value, expected):
    assert number.apnumber(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        ("foo", "foo"),
        (None, "None"),
        ("", ""),
        ([1], "[1]"),
    ],
)
def test_apnumber_invalid_returns_str(value, expected):
    assert number.apnumber(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (float("nan"), "NaN"),
        (float("inf"), "+Inf"),
        (float("-inf"), "-Inf"),
    ],
)
def test_apnumber_not_finite(value, expected):
    assert number.apnumber(value) == expected


def test_apnumber_uses_gettext_only_for_words(monkeypatch):
    monkeypatch.setattr(number, "_", lambda message: message.upper())
    assert number.apnumber(3) == "THREE"
    assert number.apnumber(0) == "ZERO"
    assert number.apnumber(10) == "10"
    assert number.apnumber(-4) == "-4"


def test_apnumber_overflow_raises():
    with pytest.raises(OverflowError):
        number.apnumber(10**400)


@pytest.mark.parametrize(
    "value, expected",
    [
        (0.3, "3/10"),
        (1.3, "1 3/10"),
        (float(1 / 3), "1/3"),
        (1, "1"),
        (0, "0/1"),
        (0.0, "0/1"),
        (0.5, "1/2"),
        (0.25, "1/4"),
        (2.5, "2 1/2"),
        (10.75, "10 3/4"),
        (1.0, "1"),
        (1.0001, "1"),
        (0.0001, "0/1"),
        (1.999, "1 999/1000"),
        (-0.5, "-1/2"),
        (-1.3, "-1 3/10"),
        (-2, "-2"),
        (-2.5, "-2 1/2"),
        ("1.5", "1 1/2"),
        ("2", "2"),
        (Fraction(1, 3), "1/3"),
    ],
)
def test_fractional_values(value, expected):
    assert number.fractional(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        ("ten", "ten"),
        (None, "None"),
        ("", ""),
        ("1/3", "1/3"),
        ([1], "[1]"),
    ],
)
def test_fractional_invalid_returns_str(value, expected):
    assert number.fractional(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (float("nan"), "NaN"),
        (float("inf"), "+Inf"),
        (float("-inf"), "-Inf"),
        ("nan", "NaN"),
    ],
)
def test_fractional_not_finite(value, expected):
    assert number.fractional(value) == expected


def test_fractional_overflow_raises():
    with pytest.raises(OverflowError):
        number.fractional(10**400)


@pytest.mark.parametrize(
    "value, expected",
    [
        (0.3, "3.00 x 10⁻¹"),
        (500, "5.00 x 10²"),
        (-1000, "-1.00 x 10³"),
        ("99", "9.90 x 10¹"),
        (0, "0.00 x 10⁰"),
        (1, "1.00 x 10⁰"),
        (1e-10, "1.00 x 10⁻¹⁰"),
        (1e100, "1.00 x 10¹⁰⁰"),
        (-0.05, "-5.00 x 10⁻²"),
        (123456, "1.23 x 10⁵"),
    ],
)
def test_scientific_values(value, expected):
    assert number.scientific(value) == expected


@pytest.mark.parametrize(
    "value, precision, expected",
    [
        (1000, 1, "1.0 x 10³"),
        (1000, 3, "1.000 x 10³"),
        (1000, 0, "1 x 10³"),
        (1234.5678, 4, "1.2346 x 10³"),
    ],
)
def test_scientific_precision(value, precision, expected):
    assert number.scientific(value, precision) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        ("foo", "foo"),
        (None, "None"),
        ("", ""),
        ([1], "[1]"),
    ],
)
def test_scientific_invalid_returns_str(value, expected):
    assert number.scientific(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (float("nan"), "NaN"),
        (float("inf"), "+Inf"),
        (float("-inf"), "-Inf"),
        ("inf", "+Inf"),
    ],
)
def test_scientific_not_finite(value, expected):
    assert number.scientific(value) == expected


def test_scientific_invalid_precision_raises():
    with pytest.raises(ValueError):
        number.scientific(1000, "x")
    with pytest.raises(ValueError):
        number.scientific(1000, -1)


def test_scientific_overflow_raises():
    with pytest.raises(OverflowError):
        number.scientific(10**400)


def test_clamp_no_limits():
    assert number.clamp(123.456) == "123.456"
    assert number.clamp(5) == "5"
    assert number.clamp(0) == "0"
    assert number.clamp(-3.5) == "-3.5"


def test_clamp_none_returns_none():
    assert number.clamp(None) is None


def test_clamp_floor():
    assert number.clamp(0.0001, floor=0.01) == "<0.01"
    assert number.clamp(-1, floor=0) == "<0"
    assert number.clamp(0.5, floor=0.01) == "0.5"


def test_clamp_ceil():
    assert number.clamp(0.99, format="{:.0%}", ceil=0.99) == "99%"
    assert number.clamp(0.999, format="{:.0%}", ceil=0.99) == ">99%"
    assert number.clamp(100, ceil=10) == ">10"
    assert number.clamp(5, ceil=10) == "5"


def test_clamp_value_equal_to_limits_is_not_clamped():
    assert number.clamp(5, floor=5) == "5"
    assert number.clamp(5, ceil=5) == "5"
    assert number.clamp(5, floor=5, ceil=5) == "5"


def test_clamp_floor_and_ceil_together():
    assert number.clamp(5, floor=1, ceil=10) == "5"
    assert number.clamp(0, floor=1, ceil=10) == "<1"
    assert number.clamp(11, floor=1, ceil=10) == ">10"


def test_clamp_custom_tokens():
    assert number.clamp(100, ceil=10, ceil_token=">>") == ">>10"
    assert number.clamp(-1, floor=0, floor_token="<<") == "<<0"
    assert number.clamp(-1, floor=0, floor_token="") == "0"


def test_clamp_callable_format():
    assert number.clamp(
        1, format=number.intword, floor=1e6, floor_token="under "
    ) == "under 1.0 million"
    assert number.clamp(5, format=lambda v: f"[{v}]") == "[5]"
    assert number.clamp(50, format=lambda v: f"[{v}]", ceil=10) == ">[10]"


def test_clamp_format_string_variants():
    assert number.clamp(3.14159, format="{:.2f}") == "3.14"
    assert number.clamp(3, format="value={}") == "value=3"


@pytest.mark.parametrize(
    "value, expected",
    [
        (float("nan"), "NaN"),
        (float("inf"), "+Inf"),
        (float("-inf"), "-Inf"),
    ],
)
def test_clamp_not_finite(value, expected):
    assert number.clamp(value) == expected
    assert number.clamp(value, floor=0, ceil=10) == expected


@pytest.mark.parametrize("bad_format", [123, None, 1.5, [], object()])
def test_clamp_invalid_format_raises(bad_format):
    with pytest.raises(ValueError, match="Invalid format"):
        number.clamp(5, format=bad_format)


def test_clamp_non_numeric_raises_type_error():
    with pytest.raises(TypeError):
        number.clamp("5")


def test_metric_docstring_examples():
    assert number.metric(1500, "V") == "1.50 kV"
    assert number.metric(2e8, "W") == "200 MW"
    assert number.metric(220e-6, "F") == "220 μF"
    assert number.metric(1e-14, precision=4) == "10.00 f"
    assert number.metric(1e40) == "1.00 x 10⁴⁰"


@pytest.mark.parametrize(
    "value, unit, expected",
    [
        (0, "", "0.00"),
        (0, "V", "0.00 V"),
        (1, "", "1.00"),
        (1, "m", "1.00 m"),
        (10, "", "10.0"),
        (100, "", "100"),
        (123000, "", "123 k"),
        (1230000, "", "1.23 M"),
        (-1500, "V", "-1.50 kV"),
        (2000, "g", "2.00 kg"),
        (0.001, "s", "1.00 ms"),
        (0.5, "V", "500 mV"),
    ],
)
def test_metric_values(value, unit, expected):
    assert number.metric(value, unit) == expected


@pytest.mark.parametrize(
    "value, precision, expected",
    [
        (1234, 2, "1.2 k"),
        (1234, 1, "1 k"),
        (1234, 0, "1 k"),
        (1234, 5, "1.2340 k"),
    ],
)
def test_metric_precision(value, precision, expected):
    assert number.metric(value, "", precision) == expected


@pytest.mark.parametrize("k", range(1, 11))
def test_metric_every_large_prefix(k):
    assert number.metric(2 * 10 ** (3 * k)) == f"2.00 {'kMGTPEZYRQ'[k - 1]}"


@pytest.mark.parametrize("k", range(1, 11))
def test_metric_every_small_prefix(k):
    assert number.metric(float(f"2e-{3 * k}")) == f"2.00 {'mμnpfazyrq'[k - 1]}"


def test_metric_rounding_steps_up_prefix():
    assert number.metric(999999) == "1.00 M"
    assert number.metric(999999, "V") == "1.00 MV"
    assert number.metric(0.999999) == "1.00"
    assert number.metric(0.999999, "V") == "1.00 V"
    assert number.metric(9.999e29) == "1.00 Q"


def test_metric_no_step_up_for_largest_exponents():
    assert number.metric(2e30) == "2.00 Q"
    assert number.metric(5e32) == "500 Q"
    assert number.metric(9.999e32) == "1000 Q"


def test_metric_falls_back_to_scientific():
    assert number.metric(1e35) == "1.00 x 10³⁵"
    assert number.metric(1e40, "W") == "1.00 x 10⁴⁰W"
    assert number.metric(1e40, precision=5) == "1.0000 x 10⁴⁰"
    assert number.metric(1e-35) == "1.00 x 10⁻³⁵"
    assert number.metric(-1e40) == "-1.00 x 10⁴⁰"


def test_metric_special_units_have_no_space():
    assert number.metric(30, "°") == "30.0°"
    assert number.metric(30, "′") == "30.0′"
    assert number.metric(30, "″") == "30.0″"
    assert number.metric(1500, "°") == "1.50k°"
    assert number.metric(0, "°") == "0.00°"


@pytest.mark.parametrize(
    "value, expected",
    [
        (float("nan"), "NaN"),
        (float("inf"), "+Inf"),
        (float("-inf"), "-Inf"),
    ],
)
def test_metric_not_finite(value, expected):
    assert number.metric(value) == expected
    assert number.metric(value, "V") == expected


def test_metric_non_numeric_raises_type_error():
    with pytest.raises(TypeError):
        number.metric("5")
    with pytest.raises(TypeError):
        number.metric(None)


def test_metric_matches_for_integers_and_floats():
    assert number.metric(2000) == number.metric(2000.0)
    assert math.isclose(float(number.metric(2500).split()[0]), 2.5)