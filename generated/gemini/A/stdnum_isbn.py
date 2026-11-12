import pytest
from stdnum.exceptions import (
    InvalidChecksum,
    InvalidComponent,
    InvalidFormat,
    InvalidLength,
)
from stdnum.isbn import (
    compact,
    _calc_isbn10_check_digit,
    validate,
    isbn_type,
    is_valid,
    to_isbn13,
    to_isbn10,
    split,
    format,
)


def test_compact():
    assert compact("1-85798-218-5") == "1857982185"
    assert compact("  978-9024538270  ") == "9789024538270"
    assert compact("857982185") == "0857982185"
    assert compact("1-85798-218-5", convert=True) == "9781857982183"


def test_calc_isbn10_check_digit():
    assert _calc_isbn10_check_digit("185798218") == "5"
    assert _calc_isbn10_check_digit("047195869") == "X"


def test_validate():
    assert validate("978-9024538270") == "9789024538270"
    assert validate("1-85798-218-5") == "1857982185"
    assert validate("1-85798-218-5", convert=True) == "9781857982183"


def test_validate_invalid_format():
    with pytest.raises(InvalidFormat):
        validate("1-85798-218-X")


def test_validate_invalid_checksum_isbn10():
    with pytest.raises(InvalidChecksum):
        validate("1-85798-218-6")


def test_validate_invalid_length():
    with pytest.raises(InvalidLength):
        validate("12345")


def test_validate_invalid_component_isbn13():
    with pytest.raises(InvalidComponent):
        validate("9779024538270")


def test_isbn_type():
    assert isbn_type("1-85798-218-5") == "ISBN10"
    assert isbn_type("978-0-471-11709-4") == "ISBN13"
    assert isbn_type("invalid") is None


def test_is_valid():
    assert is_valid("978-9024538270") is True
    assert is_valid("978-9024538271") is False


def test_to_isbn13():
    assert to_isbn13("1-85798-218-5") == "978-1-85798-218-3"
    assert to_isbn13("978-1-85798-218-3") == "978-1-85798-218-3"
    assert to_isbn13("857982185") == "9780857982183"
    assert to_isbn13("1857982185") == "9781857982183"


def test_to_isbn10():
    assert to_isbn10("1-85798-218-5") == "1-85798-218-5"
    assert to_isbn10("978-1-85798-218-3") == "1-85798-218-5"


def test_to_isbn10_exceptions():
    with pytest.raises(InvalidFormat):
        to_isbn10("not-an-isbn")
    with pytest.raises(InvalidComponent):
        to_isbn10("979-1-85798-218-3")


def test_split():
    parts_isbn10 = split("1-85798-218-5")
    assert parts_isbn10 == ("", "1", "85798", "218", "5")

    parts_isbn13 = split("978-0-471-11709-4")
    assert parts_isbn13 == ("978", "0", "471", "11709", "4")

    parts_convert = split("1-85798-218-5", convert=True)
    assert parts_convert == ("978", "1", "85798", "218", "3")


def test_format():
    assert format("9780471117094") == "978-0-471-11709-4"
    assert format("1857982185") == "1-85798-218-5"
    assert format("1857982185", separator="", convert=True) == "9781857982183"