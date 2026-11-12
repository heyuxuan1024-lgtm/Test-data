
import pytest
from unittest.mock import patch

import isbn
from stdnum.exceptions import (
    InvalidChecksum,
    InvalidComponent,
    InvalidFormat,
    InvalidLength,
    ValidationError,
)


VALID_ISBN10 = "1857982185"
VALID_ISBN10_X = "080442957X"
VALID_ISBN13 = "9780471117094"
VALID_ISBN13_979 = "9791090636071"


@pytest.mark.parametrize(
    ("number", "expected"),
    [
        ("1857982185", "1857982185"),
        ("1-85798-218-5", "1857982185"),
        ("1 85798 218 5", "1857982185"),
        ("  1-85798-218-5  ", "1857982185"),
        ("080442957x", "080442957X"),
        ("857982185", "0857982185"),
        ("  857982185  ", "0857982185"),
        ("978-0-471-11709-4", "9780471117094"),
        ("978 0 471 11709 4", "9780471117094"),
        ("979-10-90636-07-1", "9791090636071"),
    ],
)
def test_compact(number, expected):
    assert isbn.compact(number) == expected


@pytest.mark.parametrize(
    ("number", "expected"),
    [
        (VALID_ISBN10, "9781857982183"),
        ("1-85798-218-5", "9781857982183"),
        ("857982185", "9780857982180"),
        (VALID_ISBN13, VALID_ISBN13),
        ("978-0-471-11709-4", "978-0-471-11709-4"),
    ],
)
def test_compact_with_conversion(number, expected):
    assert isbn.compact(number, convert=True) == expected


@pytest.mark.parametrize(
    ("number", "expected"),
    [
        ("000000000", "0"),
        ("0000000000", "0"),
        ("123456789", "X"),
        ("080442957", "X"),
        ("185798218", "5"),
    ],
)
def test_calc_isbn10_check_digit(number, expected):
    assert isbn._calc_isbn10_check_digit(number) == expected


def test_calc_isbn10_check_digit_empty_string():
    assert isbn._calc_isbn10_check_digit("") == "0"


def test_calc_isbn10_check_digit_non_numeric_input():
    with pytest.raises(ValueError):
        isbn._calc_isbn10_check_digit("12345678X")


@pytest.mark.parametrize(
    ("number", "expected"),
    [
        (VALID_ISBN10, VALID_ISBN10),
        ("1-85798-218-5", VALID_ISBN10),
        ("080442957X", "080442957X"),
        (VALID_ISBN13, VALID_ISBN13),
        ("978-0-471-11709-4", VALID_ISBN13),
        (VALID_ISBN13_979, VALID_ISBN13_979),
    ],
)
def test_validate_valid_isbns(number, expected):
    assert isbn.validate(number) == expected


@pytest.mark.parametrize(
    "number",
    [
        "1857982184",
        "0804429570",
        "9780471117095",
    ],
)
def test_validate_invalid_checksum(number):
    with pytest.raises(InvalidChecksum):
        isbn.validate(number)


@pytest.mark.parametrize(
    "number",
    [
        "",
        "123",
        "12345678901",
        "123456789012",
        "12345678901234",
    ],
)
def test_validate_invalid_length(number):
    with pytest.raises(InvalidLength):
        isbn.validate(number)


@pytest.mark.parametrize(
    "number",
    [
        "185798218A",
        "ABCDEFGHIJ",
        "978047111709A",
        "97804711170X4",
    ],
)
def test_validate_invalid_format(number):
    with pytest.raises(InvalidFormat):
        isbn.validate(number)


@pytest.mark.parametrize(
    "number",
    [
        "1234567890128",
        "9770471117095",
        "9771234567890",
    ],
)
def test_validate_invalid_bookland_prefix(number):
    with pytest.raises(InvalidComponent):
        isbn.validate(number)


def test_validate_isbn13_ean_validation_error_propagates():
    with pytest.raises(InvalidChecksum):
        isbn.validate("9780471117095")


def test_validate_convert_isbn10():
    assert isbn.validate(VALID_ISBN10, convert=True) == "9781857982183"


def test_validate_convert_isbn10_with_separators():
    assert isbn.validate("1-85798-218-5", convert=True) == "9781857982183"


def test_validate_convert_isbn13():
    assert isbn.validate(VALID_ISBN13, convert=True) == VALID_ISBN13


@pytest.mark.parametrize(
    ("number", "expected"),
    [
        (VALID_ISBN10, "ISBN10"),
        ("1-85798-218-5", "ISBN10"),
        ("080442957X", "ISBN10"),
        (VALID_ISBN13, "ISBN13"),
        ("978-0-471-11709-4", "ISBN13"),
        (VALID_ISBN13_979, "ISBN13"),
    ],
)
def test_isbn_type_valid(number, expected):
    assert isbn.isbn_type(number) == expected


@pytest.mark.parametrize(
    "number",
    [
        "",
        "123",
        "1857982184",
        "9780471117095",
        "ABCDEFGHIJ",
        "1234567890128",
    ],
)
def test_isbn_type_invalid(number):
    assert isbn.isbn_type(number) is None


def test_isbn_type_unexpected_exception_propagates():
    with patch.object(isbn, "validate", side_effect=TypeError("unexpected")):
        with pytest.raises(TypeError):
            isbn.isbn_type(VALID_ISBN10)


@pytest.mark.parametrize(
    "number",
    [
        VALID_ISBN10,
        "1-85798-218-5",
        "080442957X",
        VALID_ISBN13,
        "978-0-471-11709-4",
        VALID_ISBN13_979,
    ],
)
def test_is_valid_true(number):
    assert isbn.is_valid(number) is True


@pytest.mark.parametrize(
    "number",
    [
        "",
        "123",
        "1857982184",
        "9780471117095",
        "ABCDEFGHIJ",
        "1234567890128",
    ],
)
def test_is_valid_false(number):
    assert isbn.is_valid(number) is False


def test_is_valid_unexpected_exception_propagates():
    with patch.object(isbn, "validate", side_effect=TypeError("unexpected")):
        with pytest.raises(TypeError):
            isbn.is_valid(VALID_ISBN10)


@pytest.mark.parametrize(
    ("number", "expected"),
    [
        ("1-85798-218-5", "978-1-85798-218-3"),
        ("1857982185", "9781857982183"),
        ("080442957X", "9780804429573"),
        ("978-0-471-11709-4", "978-0-471-11709-4"),
        ("978 0 471 11709 4", "978 0 471 11709 4"),
        ("9780471117094", "9780471117094"),
    ],
)
def test_to_isbn13(number, expected):
    assert isbn.to_isbn13(number) == expected


def test_to_isbn13_nine_digit_input():
    assert isbn.to_isbn13("857982185") == "9780857982180"


def test_to_isbn13_strips_outer_whitespace():
    assert isbn.to_isbn13(" 1-85798-218-5 ") == "978-1-85798-218-3"


def test_to_isbn13_space_separator():
    assert isbn.to_isbn13("1 85798 218 5") == "978 1 85798 218 3"


def test_to_isbn13_hyphen_separator():
    assert isbn.to_isbn13("1-85798-218-5") == "978-1-85798-218-3"


def test_to_isbn13_no_separator():
    assert isbn.to_isbn13(VALID_ISBN10) == "9781857982183"


def test_to_isbn13_invalid_short_input():
    with pytest.raises(Exception):
        isbn.to_isbn13("123")


@pytest.mark.parametrize(
    ("number", "expected"),
    [
        ("978-1-85798-218-3", "1-85798-218-5"),
        ("978 1 85798 218 3", "1 85798 218 5"),
        ("9781857982183", "1857982185"),
        ("1-85798-218-5", "1-85798-218-5"),
        ("1857982185", "1857982185"),
    ],
)
def test_to_isbn10(number, expected):
    assert isbn.to_isbn10(number) == expected


def test_to_isbn10_strips_outer_whitespace():
    assert isbn.to_isbn10(" 978-1-85798-218-3 ") == "1-85798-218-5"


def test_to_isbn10_with_space_separator():
    assert isbn.to_isbn10("978 1 85798 218 3") == "1 85798 218 5"


def test_to_isbn10_without_separator():
    assert isbn.to_isbn10("9781857982183") == "1857982185"


def test_to_isbn10_invalid_format():
    with pytest.raises(InvalidFormat):
        isbn.to_isbn10("not-an-isbn")


def test_to_isbn10_invalid_isbn13_checksum():
    with pytest.raises(InvalidFormat):
        isbn.to_isbn10("9780471117095")


def test_to_isbn10_invalid_length():
    with pytest.raises(InvalidFormat):
        isbn.to_isbn10("123456789012")


def test_to_isbn10_979_prefix():
    with pytest.raises(InvalidComponent):
        isbn.to_isbn10(VALID_ISBN13_979)


def test_to_isbn10_invalid_bookland_prefix():
    with pytest.raises(InvalidFormat):
        isbn.to_isbn10("9770471117095")


def test_to_isbn10_isbn13_without_978_prefix():
    with pytest.raises(InvalidComponent):
        isbn.to_isbn10("9791090636071")


@pytest.mark.parametrize(
    ("number", "expected"),
    [
        (
            "1-85798-218-5",
            ("", "1", "85798", "218", "5"),
        ),
        (
            "978-1-85798-218-3",
            ("978", "1", "85798", "218", "3"),
        ),
        (
            "9780471117094",
            ("978", "0", "471", "11709", "4"),
        ),
    ],
)
def test_split(number, expected):
    with patch("stdnum.numdb.get") as get:
        get.return_value.split.return_value = list(expected[1:4])
        assert isbn.split(number) == expected
        get.assert_called_once_with("isbn")


def test_split_isbn10_removes_ean_prefix():
    with patch("stdnum.numdb.get") as get:
        get.return_value.split.return_value = ["1", "85798", "218"]
        assert isbn.split(VALID_ISBN10) == (
            "",
            "1",
            "85798",
            "218",
            "5",
        )


def test_split_isbn13_keeps_ean_prefix():
    with patch("stdnum.numdb.get") as get:
        get.return_value.split.return_value = ["978", "0", "471", "11709"]
        assert isbn.split(VALID_ISBN13) == (
            "978",
            "0",
            "471",
            "11709",
            "4",
        )


def test_split_convert_true():
    with patch("stdnum.numdb.get") as get:
        get.return_value.split.return_value = ["978", "1", "85798", "218"]
        assert isbn.split(VALID_ISBN10, convert=True) == (
            "978",
            "1",
            "85798",
            "218",
            "3",
        )


@pytest.mark.parametrize(
    ("parts", "expected"),
    [
        ([], ("", "", "", "", "5")),
        (["1"], ("1", "", "", "", "5")),
        (["1", "2"], ("1", "2", "", "", "5")),
        (["1", "2", "3"], ("1", "2", "3", "", "5")),
        (["1", "2", "3", "4"], ("1", "2", "3", "4", "5")),
    ],
)
def test_split_partial_numdb_results(parts, expected):
    with patch("stdnum.numdb.get") as get:
        get.return_value.split.return_value = parts.copy()
        assert isbn.split("1857982185") == expected


def test_split_empty_result_for_isbn13():
    with patch("stdnum.numdb.get") as get:
        get.return_value.split.return_value = []
        assert isbn.split(VALID_ISBN13) == ("", "", "", "", "4")


def test_split_numdb_exception_propagates():
    with patch("stdnum.numdb.get", side_effect=LookupError("missing database")):
        with pytest.raises(LookupError):
            isbn.split(VALID_ISBN10)


def test_split_invalid_input_still_uses_compact():
    with patch("stdnum.numdb.get") as get:
        get.return_value.split.return_value = []
        result = isbn.split("123456789")
        assert result == ("", "", "", "", "9")


@pytest.mark.parametrize(
    ("number", "separator", "expected"),
    [
        ("1-85798-218-5", "-", "1-85798-218-5"),
        ("978-0-471-11709-4", "-", "978-0-471-11709-4"),
        ("978-0-471-11709-4", "", "9780471117094"),
        ("978-0-471-11709-4", " ", "978 0 471 11709 4"),
    ],
)
def test_format(number, separator, expected):
    with patch("stdnum.numdb.get") as get:
        if len(isbn.compact(number)) == 10:
            get.return_value.split.return_value = ["1", "85798", "218"]
        else:
            get.return_value.split.return_value = ["978", "0", "471", "11709"]
        assert isbn.format(number, separator=separator) == expected


def test_format_convert_true():
    with patch("stdnum.numdb.get") as get:
        get.return_value.split.return_value = ["978", "1", "85798", "218"]
        assert isbn.format(VALID_ISBN10, convert=True) == "978-1-85798-218-3"


def test_format_empty_separator_matches_compact():
    with patch("stdnum.numdb.get") as get:
        get.return_value.split.return_value = ["978", "0", "471", "11709"]
        assert isbn.format(VALID_ISBN13, separator="") == "9780471117094"


def test_format_empty_split_parts():
    with patch("stdnum.numdb.get") as get:
        get.return_value.split.return_value = []
        assert isbn.format(VALID_ISBN13) == "4"


def test_format_custom_multi_character_separator():
    with patch("stdnum.numdb.get") as get:
        get.return_value.split.return_value = ["978", "0", "471", "11709"]
        assert isbn.format(VALID_ISBN13, separator="::") == (
            "978::0::471::11709::4"
        )


def test_format_invalid_separator_type():
    with patch("stdnum.numdb.get") as get:
        get.return_value.split.return_value = []
        with pytest.raises(AttributeError):
            isbn.format(VALID_ISBN13, separator=None)


def test_compact_non_string_input():
    with pytest.raises(AttributeError):
        isbn.compact(None)


def test_validate_non_string_input():
    with pytest.raises(AttributeError):
        isbn.validate(None)


def test_to_isbn13_non_string_input():
    with pytest.raises(AttributeError):
        isbn.to_isbn13(None)


def test_to_isbn10_non_string_input():
    with pytest.raises(AttributeError):
        isbn.to_isbn10(None)


def test_split_non_string_input():
    with pytest.raises(AttributeError):
        isbn.split(None)


def test_format_non_string_input():
    with pytest.raises(AttributeError):
        isbn.format(None)


def test_validate_isbn10_x_check_digit():
    assert isbn.validate(VALID_ISBN10_X) == VALID_ISBN10_X


def test_validate_isbn10_lowercase_x():
    assert isbn.validate("080442957x") == VALID_ISBN10_X


def test_validate_isbn10_x_with_separators():
    assert isbn.validate("0-80442-957-x") == VALID_ISBN10_X


def test_isbn_type_isbn10_x():
    assert isbn.isbn_type(VALID_ISBN10_X) == "ISBN10"


def test_is_valid_isbn10_x():
    assert isbn.is_valid(VALID_ISBN10_X) is True


def test_validate_rejects_isbn10_with_x_in_body():
    with pytest.raises(InvalidFormat):
        isbn.validate("08044295X0")


def test_validate_rejects_isbn13_with_x_check_digit():
    with pytest.raises(InvalidFormat):
        isbn.validate("978047111709X")


def test_to_isbn13_isbn10_x():
    assert isbn.to_isbn13(VALID_ISBN10_X) == "9780804429573"


def test_to_isbn10_round_trip():
    isbn13 = isbn.to_isbn13(VALID_ISBN10)
    assert isbn.to_isbn10(isbn13) == VALID_ISBN10


def test_isbn13_round_trip():
    isbn10 = isbn.to_isbn10(VALID_ISBN13)
    assert isbn.to_isbn13(isbn10) == VALID_ISBN13
