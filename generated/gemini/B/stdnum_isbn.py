import pytest
from stdnum import isbn


def test_compact():
    assert isbn.compact("1-85798-218-5") == "1857982185"
    assert isbn.compact("  978-9024538270  ") == "9789024538270"
    assert isbn.compact("857982185") == "0857982185"
    assert isbn.compact("1-85798-218-5", convert=True) == "9781857982183"


def test_calc_isbn10_check_digit():
    assert isbn._calc_isbn10_check_digit("185798218") == "5"
    assert isbn._calc_isbn10_check_digit("047195869") == "X"


def test_validate():
    assert isbn.validate("978-9024538270") == "9789024538270"
    assert isbn.validate("1-85798-218-5") == "1857982185"
    assert isbn.validate("1-85798-218-5", convert=True) == "9781857982183"


def test_validate_invalid_format():
    with pytest.raises(isbn.InvalidFormat):
        isbn.validate("1-85798-218-X")


def test_validate_invalid_checksum_isbn10():
    with pytest.raises(isbn.InvalidChecksum):
        isbn.validate("1-85798-218-6")


def test_validate_invalid_length():
    with pytest.raises(isbn.InvalidLength):
        isbn.validate("12345")


def test_validate_invalid_component_isbn13():
    with pytest.raises(isbn.InvalidComponent):
        isbn.validate("9779024538270")


def test_isbn_type():
    assert isbn.isbn_type("1-85798-218-5") == "ISBN10"
    assert isbn.isbn_type("978-0-471-11709-4") == "ISBN13"
    assert isbn.isbn_type("invalid") is None


def test_is_valid():
    assert isbn.is_valid("978-9024538270") is True
    assert isbn.is_valid("978-9024538271") is False


def test_to_isbn13():
    assert isbn.to_isbn13("1-85798-218-5") == "978-1-85798-218-3"
    assert isbn.to_isbn13("978-1-85798-218-3") == "978-1-85798-218-3"
    assert isbn.to_isbn13("857982185") == "9780857982183"
    assert isbn.to_isbn13("1857982185") == "9781857982183"


def test_to_isbn10():
    assert isbn.to_isbn10("1-85798-218-5") == "1-85798-218-5"
    assert isbn.to_isbn10("978-1-85798-218-3") == "1-85798-218-5"


def test_to_isbn10_exceptions():
    with pytest.raises(isbn.InvalidFormat):
        isbn.to_isbn10("not-an-isbn")
    with pytest.raises(isbn.InvalidComponent):
        isbn.to_isbn10("979-1-85798-218-3")


def test_split():
    parts_isbn10 = isbn.split("1-85798-218-5")
    assert parts_isbn10 == ("", "1", "85798", "218", "5")

    parts_isbn13 = isbn.split("978-0-471-11709-4")
    assert parts_isbn13 == ("978", "0", "471", "11709", "4")

    parts_convert = isbn.split("1-85798-218-5", convert=True)
    assert parts_convert == ("978", "1", "85798", "218", "3")


def test_format():
    assert isbn.format("9780471117094") == "978-0-471-11709-4"
    assert isbn.format("1857982185") == "1-85798-218-5"
    assert isbn.format("1857982185", separator="", convert=True) == "9781857982183"