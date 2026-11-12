import pytest
from stdnum import iban


VALID_IBANS = [
    "GB82WEST12345698765432",
    "DE89370400440532013000",
    "FR1420041010050500013M02606",
    "BE68539007547034",
    "GR1601101050000010547023795",
    "FI2112345600000785",
]

INVALID_IBANS = [
    "",
    " ",
    "GB00WEST12345698765432",
    "GB82WEST1234569876543",
    "GB82WEST123456987654321",
    "GB82WEST1234569876543!",
    "GB82 WEST 1234 5698 7654 3",
    "ZZ89370400440532013000",
    "DE89370400440532013001",
    "12345678901234567890",
    "GB82WEST1234569876543O",
]


@pytest.mark.parametrize(
    ("number", "expected"),
    [
        ("GR16 0110 1050 0000 1054 7023 795", "GR1601101050000010547023795"),
        ("  gb82-west.1234 5698 7654 32  ", "GB82WEST12345698765432"),
        ("be31-4354.1116 1155", "BE31435411161155"),
        ("FI21 1234-5600.0000 785", "FI2112345600000785"),
        ("", ""),
        ("   ", ""),
        ("a-b.c d", "ABCD"),
    ],
)
def test_compact(number, expected):
    assert iban.compact(number) == expected


@pytest.mark.parametrize("number", VALID_IBANS)
def test_validate_known_valid_ibans(number):
    assert iban.validate(number) == number
    assert iban.is_valid(number)


@pytest.mark.parametrize("number", INVALID_IBANS)
def test_validate_invalid_ibans(number):
    with pytest.raises(iban.ValidationError):
        iban.validate(number)
    assert not iban.is_valid(number)


def test_validate_returns_compact_uppercase_value():
    assert iban.validate(" gb82 west 1234 5698 7654 32 ") == "GB82WEST12345698765432"


def test_validate_with_country_check_disabled():
    assert iban.validate("GB82 WEST 1234 5698 7654 32", check_country=False) == "GB82WEST12345698765432"
    assert iban.is_valid("GB82 WEST 1234 5698 7654 32", check_country=False)


def test_validate_checksum_is_checked_when_country_check_disabled():
    with pytest.raises(iban.ValidationError):
        iban.validate("GB00 WEST 1234 5698 7654 32", check_country=False)
    assert not iban.is_valid("GB00 WEST 1234 5698 7654 32", check_country=False)


@pytest.mark.parametrize(
    ("number", "expected"),
    [
        ("BExx435411161155", "31"),
        ("GBxxWEST12345698765432", "82"),
        ("DExx370400440532013000", "89"),
        ("FIxx123456000000785", "21"),
        ("GRxx011010500000010547023795", "16"),
    ],
)
def test_calc_check_digits(number, expected):
    assert iban.calc_check_digits(number) == expected


@pytest.mark.parametrize(
    ("number", "expected"),
    [
        ("GR1601101050000010547023795", "GR16 0110 1050 0000 1054 7023 795"),
        ("GB82WEST12345698765432", "GB82 WEST 1234 5698 7654 32"),
        ("DE89370400440532013000", "DE89 3704 0044 0532 0130 00"),
        ("BE68539007547034", "BE68 5390 0754 7034"),
        ("", ""),
        ("ABCD", "ABCD"),
    ],
)
def test_format_default_separator(number, expected):
    assert iban.format(number) == expected


@pytest.mark.parametrize(
    ("number", "separator", "expected"),
    [
        ("GB82WEST12345698765432", "-", "GB82-WEST-1234-5698-7654-32"),
        ("GB82WEST12345698765432", "", "GB82WEST12345698765432"),
        ("GB82WEST12345698765432", ".", "GB82.WEST.1234.5698.7654.32"),
        ("DE89370400440532013000", "::", "DE89::3704::0044::0532::0130::00"),
        ("", "-", ""),
    ],
)
def test_format_custom_separator(number, separator, expected):
    assert iban.format(number, separator) == expected


def test_struct_to_re_compiles_numeric_structure():
    pattern = iban._struct_to_re("2!n3!a4!c")
    assert pattern.fullmatch("12ABC1234")
    assert not pattern.fullmatch("1ABC1234")
    assert not pattern.fullmatch("12abc1234")
    assert not pattern.fullmatch("12ABC12-4")


def test_struct_to_re_supports_all_character_classes():
    pattern = iban._struct_to_re("1!n1!a1!c")
    assert pattern.fullmatch("1AZ")
    assert pattern.fullmatch("1Aa")
    assert not pattern.fullmatch("AAB")
    assert not pattern.fullmatch("1aZ")
    assert not pattern.fullmatch("1A_")


def test_struct_to_re_requires_entire_string():
    pattern = iban._struct_to_re("2!n")
    assert pattern.fullmatch("12")
    assert not pattern.fullmatch("x12")
    assert not pattern.fullmatch("123")


@pytest.mark.parametrize(
    ("structure", "value"),
    [
        ("1!n", "1"),
        ("2!n", "12"),
        ("3!a", "ABC"),
        ("4!c", "A1b2"),
        ("2!n1!a3!c", "12Axyz"),
    ],
)
def test_struct_to_re_valid_structures(structure, value):
    assert iban._struct_to_re(structure).fullmatch(value)


def test_struct_to_re_rejects_invalid_character_class():
    with pytest.raises(KeyError):
        iban._struct_to_re("2!x")


def test_struct_to_re_rejects_invalid_structure_syntax():
    pattern = iban._struct_to_re("2n")
    assert pattern.fullmatch("2n")
    assert not pattern.fullmatch("12")


def test_get_cc_module_caches_country_module():
    iban._country_modules.pop("gb", None)
    first = iban._get_cc_module("GB")
    second = iban._get_cc_module("gb")
    assert first is second
    assert "gb" in iban._country_modules


def test_get_cc_module_normalizes_country_code():
    iban._country_modules.pop("fi", None)
    assert iban._get_cc_module("FI") is iban._get_cc_module("fi")


def test_is_valid_returns_false_for_validation_errors():
    for number in INVALID_IBANS:
        assert iban.is_valid(number) is False


def test_is_valid_returns_true_for_valid_number_with_spaces():
    assert iban.is_valid("GB82 WEST 1234 5698 7654 32") is True


def test_is_valid_returns_false_when_country_check_disabled_and_checksum_invalid():
    assert iban.is_valid("GB00 WEST 1234 5698 7654 32", check_country=False) is False


@pytest.mark.parametrize(
    "number",
    [
        "GB82WEST12345698765432",
        "DE89370400440532013000",
        "BE68539007547034",
        "FI2112345600000785",
    ],
)
def test_validate_is_idempotent(number):
    assert iban.validate(iban.validate(number)) == number


def test_calc_check_digits_ignores_existing_check_digits():
    assert iban.calc_check_digits("GB00WEST12345698765432") == "82"
    assert iban.calc_check_digits("GB99WEST12345698765432") == "82"


def test_format_uses_compact_representation():
    assert iban.format(" gb82-west.1234 5698 7654 32 ") == "GB82 WEST 1234 5698 7654 32"


def test_validate_rejects_non_string_input():
    with pytest.raises((TypeError, AttributeError)):
        iban.validate(None)


def test_compact_rejects_non_string_input():
    with pytest.raises((TypeError, AttributeError)):
        iban.compact(None)


def test_format_rejects_non_string_input():
    with pytest.raises((TypeError, AttributeError)):
        iban.format(None)


def test_calc_check_digits_rejects_too_short_input():
    with pytest.raises(Exception):
        iban.calc_check_digits("AB")


def test_calc_check_digits_rejects_empty_input():
    with pytest.raises(Exception):
        iban.calc_check_digits("")


def test_validate_rejects_invalid_country_code():
    with pytest.raises(iban.ValidationError):
        iban.validate("ZZ89370400440532013000")


def test_validate_rejects_wrong_country_structure():
    with pytest.raises(iban.ValidationError):
        iban.validate("GB82WEST1234569876543")


def test_validate_rejects_lowercase_country_code_after_compaction():
    assert iban.validate("gb82west12345698765432") == "GB82WEST12345698765432"


def test_country_module_lookup_returns_none_for_unknown_country():
    iban._country_modules.pop("zz", None)
    assert iban._get_cc_module("ZZ") is None


def test_country_module_cache_contains_lowercase_keys():
    iban._country_modules.pop("de", None)
    iban._get_cc_module("DE")
    assert "de" in iban._country_modules


def test_check_country_false_skips_country_specific_validation():
    number = "GB82WEST12345698765432"
    assert iban.validate(number, check_country=False) == number


def test_check_country_true_performs_country_specific_validation():
    number = "GB82WEST12345698765432"
    assert iban.validate(number, check_country=True) == number


def test_is_valid_accepts_check_country_keyword():
    assert iban.is_valid("GB82WEST12345698765432", check_country=True)
    assert iban.is_valid("GB82WEST12345698765432", check_country=False)


def test_format_handles_non_multiple_of_four_length():
    assert iban.format("GR1601101050000010547023795") == "GR16 0110 1050 0000 1054 7023 795"


def test_compact_strips_only_allowed_separators():
    assert iban.compact("GB82-WEST.1234 5698 7654 32") == "GB82WEST12345698765432"
    assert iban.compact("GB82/WEST/1234") == "GB82/WEST/1234"
    assert iban.compact("GB82_WEST_1234") == "GB82_WEST_1234"


def test_format_empty_input_with_custom_separator():
    assert iban.format("", separator="---") == ""


def test_validate_with_surrounding_whitespace():
    assert iban.validate("\n\tGB82 WEST 1234 5698 7654 32\r\n") == "GB82WEST12345698765432"


def test_is_valid_does_not_raise_for_malformed_iban_strings():
    malformed = [
        "not an iban",
        "GB",
        "GB00",
        "GB82",
        "GB82!",
        "GB82 WEST",
        "123",
        "ZZ00INVALID",
    ]
    for number in malformed:
        assert iban.is_valid(number) is False


def test_validate_invalid_checksum_raises_validation_error():
    with pytest.raises(iban.ValidationError):
        iban.validate("GB00WEST12345698765432")


def test_validate_invalid_format_raises_validation_error():
    with pytest.raises(iban.ValidationError):
        iban.validate("GB82WEST1234569876543")


def test_validate_invalid_component_raises_validation_error():
    with pytest.raises(iban.ValidationError):
        iban.validate("ZZ89370400440532013000")