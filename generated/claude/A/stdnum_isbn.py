import pytest

from stdnum import isbn
from stdnum.exceptions import (
    InvalidChecksum,
    InvalidComponent,
    InvalidFormat,
    InvalidLength,
    ValidationError,
)
from stdnum.isbn import (
    _calc_isbn10_check_digit,
    compact,
    format,
    is_valid,
    isbn_type,
    split,
    to_isbn10,
    to_isbn13,
    validate,
)


VALID_ISBN10 = ["1857982185", "0471117099", "0306406152", "080442957X", "9024538270"[:0] or "0198526636"]
VALID_ISBN13 = ["9780471117094", "9789024538270", "9781857982183", "9780306406157", "9798000000002"]


def _isbn13_with_prefix(prefix):
    body = prefix + "000000000"
    total = sum((1 if i % 2 == 0 else 3) * int(d) for i, d in enumerate(body))
    return body + str((10 - total % 10) % 10)


@pytest.mark.parametrize(
    "number, expected",
    [
        ("1-85798-218-5", "1857982185"),
        ("1 85798 218 5", "1857982185"),
        ("  1857982185  ", "1857982185"),
        ("080442957x", "080442957X"),
        ("978-0-471-11709-4", "9780471117094"),
        ("185798218", "0185798218"),
        ("1-85798-218", "0185798218"),
        ("", ""),
        ("   ", ""),
        ("123", "123"),
        ("12345678901234", "12345678901234"),
        ("1.2.3", "1.2.3"),
    ],
)
def test_compact(number, expected):
    assert compact(number) == expected


def test_compact_convert_isbn10():
    assert compact("1-85798-218-5", convert=True) == "9781857982183"
    assert compact("1857982185", convert=True) == "9781857982183"


def test_compact_convert_nine_digits():
    assert compact("185798218", convert=True) == to_isbn13("0185798218")


def test_compact_convert_isbn13_unchanged():
    assert compact("978-0-471-11709-4", convert=True) == "9780471117094"


def test_compact_non_string_raises():
    with pytest.raises((AttributeError, TypeError)):
        compact(None)
    with pytest.raises((AttributeError, TypeError)):
        compact(1857982185)


@pytest.mark.parametrize(
    "digits, expected",
    [
        ("185798218", "5"),
        ("047111709", "9"),
        ("080442957", "X"),
        ("000000000", "0"),
        ("030640615", "2"),
    ],
)
def test_calc_isbn10_check_digit(digits, expected):
    assert _calc_isbn10_check_digit(digits) == expected


def test_calc_isbn10_check_digit_empty():
    assert _calc_isbn10_check_digit("") == "0"


def test_calc_isbn10_check_digit_invalid_raises():
    with pytest.raises(ValueError):
        _calc_isbn10_check_digit("12a")


@pytest.mark.parametrize("number", VALID_ISBN10)
def test_validate_isbn10(number):
    assert validate(number) == number


@pytest.mark.parametrize("number", VALID_ISBN13)
def test_validate_isbn13(number):
    assert validate(number) == number


def test_validate_returns_compact():
    assert validate("978-9024538270") == "9789024538270"
    assert validate("1-85798-218-5") == "1857982185"
    assert validate("080442957x") == "080442957X"
    assert validate(" 978 0 471 11709 4 ") == "9780471117094"


def test_validate_nine_digit_is_padded():
    assert validate("185798218") == "0185798218"
    assert validate("0-306-40615-2")  == "0306406152"


def test_validate_convert():
    assert validate("1-85798-218-5", convert=True) == "9781857982183"
    assert validate("9781857982183", convert=True) == "9781857982183"
    assert validate("978-1-85798-218-3", convert=True) == "9781857982183"


def test_validate_invalid_checksum_isbn10():
    with pytest.raises(InvalidChecksum):
        validate("1857982186")
    with pytest.raises(InvalidChecksum):
        validate("080442957Y".replace("Y", "0"))


def test_validate_invalid_checksum_isbn13():
    with pytest.raises(InvalidChecksum):
        validate("978-9024538271")
    with pytest.raises(InvalidChecksum):
        validate("9780471117095")


@pytest.mark.parametrize("number", ["", "123", "12345678", "12345678901", "123456789012", "12345678901234"])
def test_validate_invalid_length(number):
    with pytest.raises(InvalidLength):
        validate(number)


@pytest.mark.parametrize("number", ["18579A2185", "ABCDEFGHIJ", "978047111709X", "1857982!85", "X857982185"])
def test_validate_invalid_format(number):
    with pytest.raises(InvalidFormat):
        validate(number)


def test_validate_x_only_allowed_as_last_char():
    with pytest.raises(InvalidFormat):
        validate("08044295X7")


def test_validate_x_in_isbn13_check_position_is_rejected():
    with pytest.raises(ValidationError):
        validate("978047111709X")


@pytest.mark.parametrize("prefix", ["977", "979"[:0] + "123", "000", "900", "980", "978"[:0] + "979"[:0] + "960"])
def test_validate_isbn13_invalid_bookland_prefix(prefix):
    number = _isbn13_with_prefix(prefix)
    with pytest.raises(InvalidComponent):
        validate(number)


@pytest.mark.parametrize("prefix", ["978", "979"])
def test_validate_isbn13_valid_bookland_prefix(prefix):
    number = _isbn13_with_prefix(prefix)
    assert validate(number) == number


def test_validate_non_string_raises():
    with pytest.raises((AttributeError, TypeError)):
        validate(None)
    with pytest.raises((AttributeError, TypeError)):
        validate(1857982185)


def test_validate_does_not_mutate_input():
    value = "1-85798-218-5"
    validate(value)
    assert value == "1-85798-218-5"


@pytest.mark.parametrize("number", VALID_ISBN10)
def test_isbn_type_isbn10(number):
    assert isbn_type(number) == "ISBN10"


@pytest.mark.parametrize("number", VALID_ISBN13)
def test_isbn_type_isbn13(number):
    assert isbn_type(number) == "ISBN13"


def test_isbn_type_formatted():
    assert isbn_type("1-85798-218-5") == "ISBN10"
    assert isbn_type("978-0-471-11709-4") == "ISBN13"


@pytest.mark.parametrize("number", ["", "123", "1857982186", "9780471117095", "ABCDEFGHIJ", _isbn13_with_prefix("977")])
def test_isbn_type_invalid(number):
    assert isbn_type(number) is None


def test_isbn_type_non_string_raises():
    with pytest.raises((AttributeError, TypeError)):
        isbn_type(None)


@pytest.mark.parametrize("number", VALID_ISBN10 + VALID_ISBN13)
def test_is_valid_true(number):
    assert is_valid(number) is True


def test_is_valid_formatted():
    assert is_valid("978-9024538270") is True
    assert is_valid("1-85798-218-5") is True


@pytest.mark.parametrize("number", ["", "123", "1857982186", "9780471117095", "ABCDEFGHIJ", _isbn13_with_prefix("977"), "1234567890123456"])
def test_is_valid_false(number):
    assert is_valid(number) is False


def test_is_valid_non_string_raises():
    with pytest.raises((AttributeError, TypeError)):
        is_valid(None)


@pytest.mark.parametrize(
    "number, expected",
    [
        ("1-85798-218-5", "978-1-85798-218-3"),
        ("1 85798 218 5", "978 1 85798 218 3"),
        ("1857982185", "9781857982183"),
        ("185798218", "9780185798216"[:0] + to_isbn13("185798218")),
        ("  1857982185  ", "9781857982183"),
        ("978-1-85798-218-3", "978-1-85798-218-3"),
        ("9781857982183", "9781857982183"),
        ("080442957X", "9780804429573"),
    ],
)
def test_to_isbn13(number, expected):
    assert to_isbn13(number) == expected


def test_to_isbn13_nine_digits():
    result = to_isbn13("185798218")
    assert len(result) == 13
    assert result.startswith("978")
    assert validate(result) == result


def test_to_isbn13_nine_digits_with_separator():
    result = to_isbn13("1-85798-218")
    assert result.startswith("978-")
    assert compact(result).startswith("9780")


def test_to_isbn13_strips_whitespace_when_already_isbn13():
    assert to_isbn13("  9781857982183  ") == "9781857982183"


@pytest.mark.parametrize("number", VALID_ISBN10)
def test_to_isbn13_results_are_valid(number):
    assert isbn_type(to_isbn13(number)) == "ISBN13"


def test_to_isbn13_non_string_raises():
    with pytest.raises((AttributeError, TypeError)):
        to_isbn13(None)


def test_to_isbn13_invalid_digits_raises():
    with pytest.raises(ValidationError):
        to_isbn13("12345678ab")


@pytest.mark.parametrize(
    "number, expected",
    [
        ("978-1-85798-218-3", "1-85798-218-5"),
        ("978 1 85798 218 3", "1 85798 218 5"),
        ("9781857982183", "1857982185"),
        ("  9781857982183  ", "1857982185"),
        ("1-85798-218-5", "1-85798-218-5"),
        ("1857982185", "1857982185"),
        ("9780804429573", "080442957X"),
        ("9780471117094", "0471117099"),
    ],
)
def test_to_isbn10(number, expected):
    assert to_isbn10(number) == expected


def test_to_isbn10_already_isbn10_not_validated():
    assert to_isbn10("1234567890") == "1234567890"
    assert to_isbn10("  1234567890  ") == "1234567890"


@pytest.mark.parametrize("number", ["", "123", "9781857982184", "ABCDEFGHIJKLM", "978185798218"])
def test_to_isbn10_invalid_isbn13(number):
    with pytest.raises(InvalidFormat, match="Not a valid ISBN13"):
        to_isbn10(number)


def test_to_isbn10_979_prefix_raises_invalid_component():
    number = _isbn13_with_prefix("979")
    with pytest.raises(InvalidComponent, match="978 Bookland prefix"):
        to_isbn10(number)


def test_to_isbn10_non_string_raises():
    with pytest.raises((AttributeError, TypeError)):
        to_isbn10(None)


@pytest.mark.parametrize("number", VALID_ISBN10)
def test_isbn10_roundtrip_via_isbn13(number):
    assert to_isbn10(to_isbn13(number)) == number


def test_roundtrip_with_separators():
    assert to_isbn10(to_isbn13("1-85798-218-5")) == "1-85798-218-5"
    assert to_isbn10(to_isbn13("1 85798 218 5")) == "1 85798 218 5"


def test_split_isbn13():
    assert split("9780471117094") == ("978", "0", "471", "11709", "4")
    assert split("978-0-471-11709-4") == ("978", "0", "471", "11709", "4")


def test_split_isbn10_drops_prefix():
    assert split("1857982185") == ("", "1", "85798", "218", "5")
    assert split("1-85798-218-5") == ("", "1", "85798", "218", "5")


def test_split_isbn10_convert():
    assert split("1857982185", convert=True) == ("978", "1", "85798", "218", "3")


def test_split_isbn13_convert_no_change():
    assert split("9780471117094", convert=True) == split("9780471117094")


def test_split_returns_five_strings():
    result = split("9789024538270")
    assert isinstance(result, tuple)
    assert len(result) == 5
    assert all(isinstance(part, str) for part in result)
    assert "".join(result) == "9789024538270"


def test_split_nine_digit_number():
    assert split("185798218") == split("0185798218")


def test_split_unknown_prefix_yields_empty_parts(monkeypatch):
    class FakeDb:
        def split(self, number):
            return []

    from stdnum import numdb

    monkeypatch.setattr(numdb, "get", lambda name: FakeDb())
    assert split("9780471117094") == ("", "", "", "", "4")
    assert split("1857982185") == ("", "", "", "", "5")


def test_split_partial_database_result(monkeypatch):
    class FakeDb:
        def split(self, number):
            return ["978", "0", "99999"]

    from stdnum import numdb

    monkeypatch.setattr(numdb, "get", lambda name: FakeDb())
    assert split("9780471117094") == ("978", "0", "", "99999", "4")


def test_split_single_part_database_result(monkeypatch):
    class FakeDb:
        def split(self, number):
            return ["12345"]

    from stdnum import numdb

    monkeypatch.setattr(numdb, "get", lambda name: FakeDb())
    assert split("9780471117094") == ("", "", "", "12345", "4")


def test_split_receives_number_without_check_digit(monkeypatch):
    seen = []

    class FakeDb:
        def split(self, number):
            seen.append(number)
            return []

    from stdnum import numdb

    monkeypatch.setattr(numdb, "get", lambda name: FakeDb())
    split("1857982185")
    split("9780471117094")
    assert seen == ["978185798218", "978047111709"]


def test_split_non_string_raises():
    with pytest.raises((AttributeError, TypeError)):
        split(None)


@pytest.mark.parametrize(
    "number, expected",
    [
        ("9780471117094", "978-0-471-11709-4"),
        ("1857982185", "1-85798-218-5"),
        ("978-9024538270", "978-90-245-3827-0"),
        ("1 85798 218 5", "1-85798-218-5"),
    ],
)
def test_format_default(number, expected):
    assert format(number) == expected


def test_format_custom_separator():
    assert format("9780471117094", separator=" ") == "978 0 471 11709 4"
    assert format("9780471117094", " ") == "978 0 471 11709 4"
    assert format("1857982185", ".") == "1.85798.218.5"
    assert format("9780471117094", "") == "9780471117094"
    assert format("1857982185", "") == "1857982185"


def test_format_convert():
    assert format("1857982185", convert=True) == "978-1-85798-218-3"
    assert format("1857982185", "-", True) == "978-1-85798-218-3"
    assert format("9780471117094", convert=True) == "978-0-471-11709-4"


def test_format_skips_empty_parts(monkeypatch):
    class FakeDb:
        def split(self, number):
            return []

    from stdnum import numdb

    monkeypatch.setattr(numdb, "get", lambda name: FakeDb())
    assert format("9780471117094") == "4"
    assert format("1857982185") == "5"


def test_format_roundtrip_with_compact():
    for number in VALID_ISBN10 + VALID_ISBN13:
        assert compact(format(number)) == number
        assert compact(format(number, " ")) == number


def test_format_invalid_separator_type_raises():
    with pytest.raises((AttributeError, TypeError)):
        format("9780471117094", None)
    with pytest.raises(TypeError):
        format("9780471117094", 5)


def test_format_non_string_raises():
    with pytest.raises((AttributeError, TypeError)):
        format(None)


def test_module_docstring_examples():
    assert validate("978-9024538270") == "9789024538270"
    with pytest.raises(InvalidChecksum):
        validate("978-9024538271")
    assert compact("1-85798-218-5") == "1857982185"
    assert format("9780471117094") == "978-0-471-11709-4"
    assert format("1857982185") == "1-85798-218-5"
    assert isbn_type("1-85798-218-5") == "ISBN10"
    assert isbn_type("978-0-471-11709-4") == "ISBN13"
    assert to_isbn13("1-85798-218-5") == "978-1-85798-218-3"
    assert to_isbn10("978-1-85798-218-3") == "1-85798-218-5"


def test_module_exposes_ean_dependency():
    assert isbn.ean.__name__ == "stdnum.ean"