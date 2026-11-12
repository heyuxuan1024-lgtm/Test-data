
import pytest
import iban
from stdnum.exceptions import (
    InvalidComponent,
    InvalidFormat,
    InvalidChecksum,
    ValidationError,
)


VALID_BE = "BE68539007547034"
VALID_GR = "GR1601101050000010547023795"


@pytest.fixture(autouse=True)
def clear_country_module_cache():
    iban._country_modules.clear()
    yield
    iban._country_modules.clear()


def test_compact_removes_valid_separators_and_whitespace():
    assert iban.compact("  gr16 0110-1050.0000 1054 7023 795  ") == VALID_GR


@pytest.mark.parametrize(
    "number, expected",
    [
        ("BE68 5390 0754 7034", VALID_BE),
        ("be68-5390-0754-7034", VALID_BE),
        ("  BE68.5390.0754.7034  ", VALID_BE),
        ("", ""),
        ("  ", ""),
        ("AB-CD. ef", "ABCDEF"),
    ],
)
def test_compact(number, expected):
    assert iban.compact(number) == expected


def test_calc_check_digits():
    assert iban.calc_check_digits("BExx435411161155") == "31"


def test_calc_check_digits_ignores_existing_check_digits():
    assert iban.calc_check_digits("BE68539007547034") == "68"


def test_calc_check_digits_with_lowercase_and_separators():
    assert iban.calc_check_digits("be--xx 4354 1116 1155") == "31"


def test_calc_check_digits_short_input():
    with pytest.raises((IndexError, ValueError)):
        iban.calc_check_digits("")


@pytest.mark.parametrize(
    "structure, value, expected",
    [
        ("2!a", "BE", True),
        ("2!a", "Be", False),
        ("2!n", "12", True),
        ("2!n", "1A", False),
        ("2!c", "A1", True),
        ("2!c", "aZ", True),
        ("2!c", "A-", False),
        ("2!n2!a", "12AB", True),
        ("2!n2!a", "12A1", False),
        ("4!n", "1234", True),
        ("4!n", "123", False),
        ("", "", True),
    ],
)
def test_struct_to_re(structure, value, expected):
    regex = iban._struct_to_re(structure)
    assert bool(regex.match(value)) is expected


def test_struct_to_re_anchors_entire_string():
    regex = iban._struct_to_re("2!n")
    assert regex.match("12")
    assert regex.match("012") is None
    assert regex.match("12\n") is None


def test_struct_to_re_invalid_character_type():
    with pytest.raises(KeyError):
        iban._struct_to_re("2!x")


def test_struct_to_re_invalid_structure_without_type():
    regex = iban._struct_to_re("invalid")
    assert regex.match("invalid")


def test_get_cc_module_converts_country_code_to_lowercase(monkeypatch):
    calls = []

    def fake_get_cc_module(cc, module_name):
        calls.append((cc, module_name))
        return object()

    monkeypatch.setattr(iban, "get_cc_module", fake_get_cc_module)

    first = iban._get_cc_module("BE")
    second = iban._get_cc_module("be")

    assert first is second
    assert calls == [("be", "iban")]


def test_get_cc_module_caches_none(monkeypatch):
    calls = []

    def fake_get_cc_module(cc, module_name):
        calls.append((cc, module_name))
        return None

    monkeypatch.setattr(iban, "get_cc_module", fake_get_cc_module)

    assert iban._get_cc_module("XX") is None
    assert iban._get_cc_module("xx") is None
    assert calls == [("xx", "iban")]


def test_get_cc_module_different_country_codes_are_cached_separately(monkeypatch):
    calls = []

    def fake_get_cc_module(cc, module_name):
        calls.append(cc)
        return cc

    monkeypatch.setattr(iban, "get_cc_module", fake_get_cc_module)

    assert iban._get_cc_module("BE") == "be"
    assert iban._get_cc_module("DE") == "de"
    assert calls == ["be", "de"]


def configure_validation(monkeypatch, structure="12!n", country_module=None):
    monkeypatch.setattr(
        iban._ibandb,
        "info",
        lambda number: [(None, {"bban": structure})],
    )
    monkeypatch.setattr(iban, "_get_cc_module", lambda cc: country_module)


def test_validate_valid_belgian_iban_without_country_module(monkeypatch):
    configure_validation(monkeypatch)
    assert iban.validate(VALID_BE) == VALID_BE


def test_validate_valid_greek_iban_without_country_module(monkeypatch):
    configure_validation(monkeypatch, structure="23!n")
    assert iban.validate(VALID_GR) == VALID_GR


def test_validate_compacts_input_before_validation(monkeypatch):
    configure_validation(monkeypatch)
    assert iban.validate(" be68 5390 0754 7034 ") == VALID_BE


def test_validate_calls_country_module_when_enabled(monkeypatch):
    calls = []

    class CountryModule:
        def validate(self, number):
            calls.append(number)
            return number

    module = CountryModule()
    configure_validation(monkeypatch, country_module=module)

    assert iban.validate(VALID_BE) == VALID_BE
    assert calls == [VALID_BE]


def test_validate_skips_country_module_when_disabled(monkeypatch):
    calls = []

    class CountryModule:
        def validate(self, number):
            calls.append(number)

    configure_validation(monkeypatch, country_module=CountryModule())

    assert iban.validate(VALID_BE, check_country=False) == VALID_BE
    assert calls == []


def test_validate_skips_country_module_when_module_is_missing(monkeypatch):
    configure_validation(monkeypatch, country_module=None)
    assert iban.validate(VALID_BE) == VALID_BE


def test_validate_raises_invalid_component_when_country_is_unknown(monkeypatch):
    monkeypatch.setattr(
        iban._ibandb,
        "info",
        lambda number: [(None, None)],
    )

    with pytest.raises(InvalidComponent):
        iban.validate(VALID_BE)


def test_validate_raises_invalid_component_when_country_info_is_empty(monkeypatch):
    monkeypatch.setattr(
        iban._ibandb,
        "info",
        lambda number: [(None, {})],
    )

    with pytest.raises(InvalidComponent):
        iban.validate(VALID_BE)


@pytest.mark.parametrize(
    "structure",
    [
        "11!n",
        "13!n",
        "10!n2!a",
        "12!a",
        "12!c",
        "",
    ],
)
def test_validate_rejects_incorrect_bban_structure(monkeypatch, structure):
    configure_validation(monkeypatch, structure=structure)

    with pytest.raises(InvalidFormat):
        iban.validate(VALID_BE, check_country=False)


def test_validate_propagates_checksum_error(monkeypatch):
    def fail_checksum(number):
        raise InvalidChecksum()

    monkeypatch.setattr(iban.mod_97_10, "validate", fail_checksum)

    with pytest.raises(InvalidChecksum):
        iban.validate(VALID_BE)


def test_validate_propagates_database_error(monkeypatch):
    def fail_info(number):
        raise RuntimeError("database failure")

    monkeypatch.setattr(iban._ibandb, "info", fail_info)

    with pytest.raises(RuntimeError, match="database failure"):
        iban.validate(VALID_BE)


def test_validate_propagates_country_module_validation_error(monkeypatch):
    class CountryModule:
        def validate(self, number):
            raise InvalidFormat()

    configure_validation(monkeypatch, country_module=CountryModule())

    with pytest.raises(InvalidFormat):
        iban.validate(VALID_BE)


def test_validate_propagates_country_module_runtime_error(monkeypatch):
    class CountryModule:
        def validate(self, number):
            raise RuntimeError("country validation failure")

    configure_validation(monkeypatch, country_module=CountryModule())

    with pytest.raises(RuntimeError, match="country validation failure"):
        iban.validate(VALID_BE)


def test_validate_empty_input_raises_validation_error():
    with pytest.raises(ValidationError):
        iban.validate("")


@pytest.mark.parametrize(
    "number",
    [
        "",
        " ",
        "not an iban",
        "BE68539007547035",
        "BE6853900754703",
        "1234567890123456",
    ],
)
def test_is_valid_returns_false_for_invalid_ibans(number):
    assert iban.is_valid(number) is False


@pytest.mark.parametrize(
    "number",
    [
        VALID_BE,
        "BE68 5390 0754 7034",
        VALID_GR,
        "GR16 0110 1050 0000 1054 7023 795",
    ],
)
def test_is_valid_returns_true_for_valid_ibans(number):
    assert iban.is_valid(number) is True


def test_is_valid_returns_false_when_country_module_rejects(monkeypatch):
    class CountryModule:
        def validate(self, number):
            raise InvalidFormat()

    configure_validation(monkeypatch, country_module=CountryModule())

    assert iban.is_valid(VALID_BE) is False


def test_is_valid_returns_true_when_country_check_is_disabled(monkeypatch):
    class CountryModule:
        def validate(self, number):
            raise InvalidFormat()

    configure_validation(monkeypatch, country_module=CountryModule())

    assert iban.is_valid(VALID_BE, check_country=False) is True


def test_is_valid_does_not_suppress_non_validation_exceptions(monkeypatch):
    def fail_checksum(number):
        raise RuntimeError("unexpected failure")

    monkeypatch.setattr(iban.mod_97_10, "validate", fail_checksum)

    with pytest.raises(RuntimeError, match="unexpected failure"):
        iban.is_valid(VALID_BE)


@pytest.mark.parametrize(
    "number, separator, expected",
    [
        (VALID_GR, " ", "GR16 0110 1050 0000 1054 7023 795"),
        (VALID_BE, " ", "BE68 5390 0754 7034"),
        (VALID_BE, "-", "BE68-5390-0754-7034"),
        (VALID_BE, "", VALID_BE),
        (VALID_BE, ".", "BE68.5390.0754.7034"),
        ("", " ", ""),
        ("ABC", " ", "ABC"),
        ("ABCDEFGHI", " ", "ABCD EFGH I"),
    ],
)
def test_format(number, separator, expected):
    assert iban.format(number, separator) == expected


def test_format_compacts_input_before_formatting():
    assert iban.format(" be68-5390.0754 7034 ") == "BE68 5390 0754 7034"


def test_format_supports_multicharacter_separator():
    assert iban.format(VALID_BE, " :: ") == "BE68 :: 5390 :: 0754 :: 7034"


def test_format_supports_non_string_separator():
    with pytest.raises(TypeError):
        iban.format(VALID_BE, None)


def test_validate_database_info_with_missing_bban_key(monkeypatch):
    monkeypatch.setattr(
        iban._ibandb,
        "info",
        lambda number: [(None, {})],
    )

    with pytest.raises(InvalidFormat):
        iban.validate(VALID_BE, check_country=False)


def test_validate_database_info_with_malformed_result(monkeypatch):
    monkeypatch.setattr(
        iban._ibandb,
        "info",
        lambda number: [],
    )

    with pytest.raises(IndexError):
        iban.validate(VALID_BE)


def test_validate_database_info_with_missing_tuple_element(monkeypatch):
    monkeypatch.setattr(
        iban._ibandb,
        "info",
        lambda number: [(None,)],
    )

    with pytest.raises(IndexError):
        iban.validate(VALID_BE)
