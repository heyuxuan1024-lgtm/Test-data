import pytest
from stdnum import isbn


VALID_ISBN10 = [
    "1857982185",
    "0306406152",
    "0131103628",
    "0201633612",
    "080442957X",
    "097522980X",
    "0000000000",
]

VALID_ISBN13 = [
    "9780471117094",
    "9789024538270",
    "9781857982187",
    "9791090636071",
    "9780306406157",
]

INVALID_ISBNS = [
    "",
    " ",
    "123",
    "123456789",
    "12345678901",
    "123456789012",
    "12345678901234",
    "1857982184",
    "0306406153",
    "9780471117095",
    "9789024538271",
    "9780306406158",
    "978902453827X",
    "97890245382A0",
    "9791090636072",
    "9770471117094",
]


@pytest.mark.parametrize(
    ("number", "expected"),
    [
        ("1-85798-218-5", "1857982185"),
        ("978-0-471-11709-4", "9780471117094"),
        ("  0-306-40615-2  ", "0306406152"),
        ("080442957x", "080442957X"),
        ("123456789", "0123456789"),
        ("", ""),
        ("   ", ""),
        ("1 85798 218 5", "1857982185"),
    ],
)
def test_compact(number, expected):
    assert isbn.compact(number) == expected


@pytest.mark.parametrize(
    ("number", "expected"),
    [
        ("1-85798-218-5", "9781857982187"),
        ("1857982185", "9781857982187"),
        ("0306406152", "9780306406157"),
        ("0-306-40615-2", "9780306406157"),
        ("080442957X", "9780804429573"),
        ("9780471117094", "9780471117094"),
    ],
)
def test_compact_convert_to_isbn13(number, expected):
    assert isbn.compact(number, convert=True) == expected


@pytest.mark.parametrize("number", VALID_ISBN10 + VALID_ISBN13)
def test_validate_valid_isbns(number):
    assert isbn.validate(number) == number
    assert isbn.is_valid(number)


@pytest.mark.parametrize("number", VALID_ISBN10 + VALID_ISBN13)
def test_validate_accepts_formatted_isbns(number):
    formatted = isbn.format(number)
    assert isbn.validate(formatted) == number
    assert isbn.is_valid(formatted)


@pytest.mark.parametrize("number", INVALID_ISBNS)
def test_validate_invalid_isbns(number):
    with pytest.raises(isbn.ValidationError):
        isbn.validate(number)
    assert isbn.is_valid(number) is False


@pytest.mark.parametrize(
    ("number", "expected"),
    [
        ("1-85798-218-5", "9781857982187"),
        ("1857982185", "9781857982187"),
        ("9780471117094", "9780471117094"),
        ("978-0-471-11709-4", "9780471117094"),
    ],
)
def test_validate_convert_to_isbn13(number, expected):
    assert isbn.validate(number, convert=True) == expected


def test_validate_isbn10_with_x_check_digit():
    assert isbn.validate("080442957X") == "080442957X"
    assert isbn.is_valid("080442957X")


def test_validate_isbn10_lowercase_x_check_digit():
    assert isbn.validate("080442957x") == "080442957X"


def test_validate_rejects_invalid_isbn10_checksum():
    with pytest.raises(isbn.InvalidChecksum):
        isbn.validate("1857982184")


def test_validate_rejects_invalid_isbn13_checksum():
    with pytest.raises(isbn.InvalidChecksum):
        isbn.validate("9780471117095")


def test_validate_rejects_non_digit_isbn_body():
    with pytest.raises(isbn.InvalidFormat):
        isbn.validate("18579821A5")


def test_validate_rejects_non_digit_isbn13_body():
    with pytest.raises(isbn.InvalidFormat):
        isbn.validate("97804711170A4")


def test_validate_rejects_invalid_length():
    for number in ("", "123456789", "12345678901", "123456789012"):
        with pytest.raises(isbn.InvalidLength):
            isbn.validate(number)


def test_validate_rejects_invalid_bookland_prefix():
    number = "9770471117094"
    with pytest.raises(isbn.InvalidComponent):
        isbn.validate(number)


def test_validate_accepts_978_prefix():
    assert isbn.validate("9780471117094") == "9780471117094"


def test_validate_accepts_979_prefix():
    assert isbn.validate("9791090636071") == "9791090636071"


def test_validate_979_isbn_with_convert_enabled():
    assert isbn.validate("9791090636071", convert=True) == "9791090636071"


@pytest.mark.parametrize(
    ("number", "expected"),
    [
        ("1-85798-218-5", "ISBN10"),
        ("1857982185", "ISBN10"),
        ("080442957X", "ISBN10"),
        ("9780471117094", "ISBN13"),
        ("978-0-471-11709-4", "ISBN13"),
        ("9791090636071", "ISBN13"),
    ],
)
def test_isbn_type_valid_numbers(number, expected):
    assert isbn.isbn_type(number) == expected


@pytest.mark.parametrize("number", INVALID_ISBNS)
def test_isbn_type_invalid_numbers(number):
    assert isbn.isbn_type(number) is None


@pytest.mark.parametrize("number", VALID_ISBN10 + VALID_ISBN13)
def test_is_valid_returns_true_for_valid_numbers(number):
    assert isbn.is_valid(number) is True


@pytest.mark.parametrize("number", INVALID_ISBNS)
def test_is_valid_returns_false_for_invalid_numbers(number):
    assert isbn.is_valid(number) is False


@pytest.mark.parametrize(
    ("number", "expected"),
    [
        ("1857982185", "9781857982187"),
        ("1-85798-218-5", "978-1-85798-218-7"),
        ("1 85798 218 5", "978 1 85798 218 7"),
        ("9780471117094", "9780471117094"),
        ("978-0-471-11709-4", "978-0-471-11709-4"),
        ("0306406152", "9780306406157"),
    ],
)
def test_to_isbn13(number, expected):
    assert isbn.to_isbn13(number) == expected


def test_to_isbn13_preserves_existing_isbn13():
    number = "978-0-471-11709-4"
    assert isbn.to_isbn13(number) == number


def test_to_isbn13_preserves_existing_isbn13_without_separator():
    number = "9780471117094"
    assert isbn.to_isbn13(number) == number


def test_to_isbn13_converts_nine_digit_input():
    assert isbn.to_isbn13("857982185") == "9780857982187"


def test_to_isbn13_preserves_hyphen_separator():
    assert isbn.to_isbn13("1-85798-218-5") == "978-1-85798-218-7"


def test_to_isbn13_preserves_space_separator():
    assert isbn.to_isbn13("1 85798 218 5") == "978 1 85798 218 7"


def test_to_isbn13_without_separator():
    assert isbn.to_isbn13("1857982185") == "9781857982187"


@pytest.mark.parametrize(
    ("number", "expected"),
    [
        ("978-1-85798-218-7", "1-85798-218-5"),
        ("9781857982187", "1857982185"),
        ("978 1 85798 218 7", "1 85798 218 5"),
        ("978-0-471-11709-4", "0-471-11709-4"),
        ("9780471117094", "0471117094"),
    ],
)
def test_to_isbn10(number, expected):
    assert isbn.to_isbn10(number) == expected


def test_to_isbn10_preserves_existing_isbn10():
    number = "1-85798-218-5"
    assert isbn.to_isbn10(number) == number


def test_to_isbn10_preserves_existing_isbn10_without_separator():
    number = "1857982185"
    assert isbn.to_isbn10(number) == number


def test_to_isbn10_rejects_invalid_isbn13():
    with pytest.raises(isbn.InvalidFormat):
        isbn.to_isbn10("9780471117095")


def test_to_isbn10_rejects_isbn10_input_with_invalid_checksum():
    with pytest.raises(isbn.InvalidFormat):
        isbn.to_isbn10("9780471117095")


def test_to_isbn10_rejects_979_prefix():
    with pytest.raises(isbn.InvalidComponent):
        isbn.to_isbn10("9791090636071")


def test_to_isbn10_rejects_invalid_length():
    with pytest.raises(isbn.InvalidFormat):
        isbn.to_isbn10("123456789012")


def test_to_isbn10_rejects_non_isbn13_input():
    with pytest.raises(isbn.InvalidFormat):
        isbn.to_isbn10("not-an-isbn")


@pytest.mark.parametrize(
    ("number", "expected"),
    [
        ("1-85798-218-5", ("", "1", "85798", "218", "5")),
        ("1857982185", ("", "1", "85798", "218", "5")),
        ("978-1-85798-218-7", ("978", "1", "85798", "218", "7")),
        ("9781857982187", ("978", "1", "85798", "218", "7")),
        ("978-0-471-11709-4", ("978", "0", "471", "11709", "4")),
        ("9780471117094", ("978", "0", "471", "11709", "4")),
    ],
)
def test_split(number, expected):
    assert isbn.split(number) == expected


def test_split_converts_isbn10_when_requested():
    assert isbn.split("1-85798-218-5", convert=True) == (
        "978",
        "1",
        "85798",
        "218",
        "7",
    )


def test_split_isbn10_returns_empty_ean_prefix():
    result = isbn.split("1857982185")
    assert result[0] == ""
    assert result[-1] == "5"


def test_split_isbn13_returns_bookland_prefix():
    result = isbn.split("9781857982187")
    assert result[0] == "978"


def test_split_returns_five_components():
    result = isbn.split("9780471117094")
    assert len(result) == 5


@pytest.mark.parametrize(
    ("number", "expected"),
    [
        ("1-85798-218-5", "1-85798-218-5"),
        ("1857982185", "1-85798-218-5"),
        ("9780471117094", "978-0-471-11709-4"),
        ("978-0-471-11709-4", "978-0-471-11709-4"),
        ("9781857982187", "978-1-85798-218-7"),
    ],
)
def test_format_default_separator(number, expected):
    assert isbn.format(number) == expected


@pytest.mark.parametrize(
    ("number", "separator", "expected"),
    [
        ("9780471117094", " ", "978 0 471 11709 4"),
        ("9780471117094", ".", "978.0.471.11709.4"),
        ("9780471117094", "", "9780471117094"),
        ("1857982185", " ", "1 85798 218 5"),
        ("9781857982187", "::", "978::1::85798::218::7"),
    ],
)
def test_format_custom_separator(number, separator, expected):
    assert isbn.format(number, separator) == expected


def test_format_convert_isbn10_to_isbn13():
    assert isbn.format("1-85798-218-5", convert=True) == "978-1-85798-218-7"


def test_format_convert_isbn13():
    assert isbn.format("9780471117094", convert=True) == "978-0-471-11709-4"


def test_format_empty_separator_matches_compact():
    assert isbn.format("1-85798-218-5", separator="") == isbn.compact("1-85798-218-5")


def test_format_omits_empty_components():
    result = isbn.format("1857982185")
    assert result == "1-85798-218-5"


def test_compact_handles_lowercase_x():
    assert isbn.compact("0-8044-2957-x") == "080442957X"


def test_compact_preserves_other_characters_for_validation():
    assert isbn.compact("18579821/5") == "18579821/5"


def test_validate_rejects_slashes():
    with pytest.raises(isbn.InvalidFormat):
        isbn.validate("18579821/5")


def test_validate_rejects_letters_in_isbn13():
    with pytest.raises(isbn.InvalidFormat):
        isbn.validate("97804711170A4")


def test_validate_rejects_x_in_isbn13():
    with pytest.raises(isbn.InvalidFormat):
        isbn.validate("978047111709X")


def test_validate_accepts_whitespace_and_hyphens():
    assert isbn.validate(" 1-85798-218-5 ") == "1857982185"


def test_isbn_type_accepts_formatted_isbn10():
    assert isbn.isbn_type("1-85798-218-5") == "ISBN10"


def test_isbn_type_accepts_formatted_isbn13():
    assert isbn.isbn_type("978-0-471-11709-4") == "ISBN13"


def test_to_isbn13_handles_nine_digit_input_with_hyphens():
    assert isbn.to_isbn13("857-982-185") == "9780857982187"


def test_to_isbn10_handles_surrounding_whitespace():
    assert isbn.to_isbn10(" 978-1-85798-218-7 ") == "1-85798-218-5"


def test_validate_rejects_non_string_input():
    with pytest.raises((TypeError, AttributeError)):
        isbn.validate(None)


def test_compact_rejects_non_string_input():
    with pytest.raises((TypeError, AttributeError)):
        isbn.compact(None)


def test_format_rejects_non_string_input():
    with pytest.raises((TypeError, AttributeError)):
        isbn.format(None)


def test_to_isbn13_rejects_non_string_input():
    with pytest.raises((TypeError, AttributeError)):
        isbn.to_isbn13(None)


def test_to_isbn10_rejects_non_string_input():
    with pytest.raises((TypeError, AttributeError)):
        isbn.to_isbn10(None)


def test_split_rejects_non_string_input():
    with pytest.raises((TypeError, AttributeError)):
        isbn.split(None)


def test_calc_isbn10_check_digit_valid_values():
    assert isbn._calc_isbn10_check_digit("185798218") == "5"
    assert isbn._calc_isbn10_check_digit("080442957") == "X"
    assert isbn._calc_isbn10_check_digit("030640615") == "2"


def test_calc_isbn10_check_digit_zero_result():
    assert isbn._calc_isbn10_check_digit("000000000") == "0"


def test_calc_isbn10_check_digit_rejects_non_digit():
    with pytest.raises(ValueError):
        isbn._calc_isbn10_check_digit("12345678A")


def test_calc_isbn10_check_digit_rejects_empty_input():
    assert isbn._calc_isbn10_check_digit("") == "0"


def test_to_isbn10_preserves_hyphen_separator():
    assert isbn.to_isbn10("978-1-85798-218-7") == "1-85798-218-5"


def test_to_isbn10_preserves_space_separator():
    assert isbn.to_isbn10("978 1 85798 218 7") == "1 85798 218 5"


def test_to_isbn10_without_separator():
    assert isbn.to_isbn10("9781857982187") == "1857982185"


def test_split_with_convert_preserves_isbn13_components():
    assert isbn.split("9780471117094", convert=True) == (
        "978",
        "0",
        "471",
        "11709",
        "4",
    )


def test_is_valid_handles_formatted_isbns():
    assert isbn.is_valid("1-85798-218-5")
    assert isbn.is_valid("978-0-471-11709-4")


def test_isbn_type_returns_none_for_bad_checksum():
    assert isbn.isbn_type("1857982184") is None
    assert isbn.isbn_type("9780471117095") is None


def test_validate_rejects_isbn10_with_non_digit_check_character():
    with pytest.raises(isbn.InvalidFormat):
        isbn.validate("185798218A")


def test_validate_rejects_isbn10_with_invalid_x_position():
    with pytest.raises(isbn.InvalidFormat):
        isbn.validate("X857982185")


def test_to_isbn13_preserves_hyphenated_isbn13():
    number = "978-0-471-11709-4"
    assert isbn.to_isbn13(number) == number


def test_to_isbn13_preserves_spaced_isbn13():
    number = "978 0 471 11709 4"
    assert isbn.to_isbn13(number) == number


def test_to_isbn10_rejects_979_even_when_checksum_is_valid():
    with pytest.raises(isbn.InvalidComponent):
        isbn.to_isbn10("9791090636071")


def test_format_with_custom_separator_and_conversion():
    assert isbn.format("1857982185", separator=" ", convert=True) == "978 1 85798 218 7"