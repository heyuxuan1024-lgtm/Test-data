import re

import pytest

from stdnum import iban
from stdnum.exceptions import (
    InvalidChecksum,
    InvalidComponent,
    InvalidFormat,
    InvalidLength,
    ValidationError,
)
from stdnum.iban import (
    _get_cc_module,
    _struct_to_re,
    calc_check_digits,
    compact,
    format,
    is_valid,
    validate,
)


VALID_IBANS = [
    "GR1601101050000010547023795",
    "BE31435411161155",
    "DE89370400440532013000",
    "GB29NWBK60161331926819",
    "FR1420041010050500013M02606",
    "NL91ABNA0417164300",
    "ES9121000418450200051332",
    "IT60X0542811101000000123456",
    "CH9300762011623852957",
    "NO9386011117947",
]


@pytest.fixture(autouse=True)
def clear_module_cache():
    iban._country_modules.clear()
    yield
    iban._country_modules.clear()


class _FakeModule:
    def __init__(self, error=None):
        self.error = error
        self.calls = []

    def validate(self, number):
        self.calls.append(number)
        if self.error is not None:
            raise self.error


@pytest.mark.parametrize(
    "number, expected",
    [
        ("GR16 0110 1050 0000 1054 7023 795", "GR1601101050000010547023795"),
        ("gr16-0110-1050-0000-1054-7023-795", "GR1601101050000010547023795"),
        ("  be31.4354.1116.1155  ", "BE31435411161155"),
        ("BE31435411161155", "BE31435411161155"),
        ("be31435411161155", "BE31435411161155"),
        ("", ""),
        ("   ", ""),
        (" - . ", ""),
        ("a b-c.d", "ABCD"),
    ],
)
def test_compact(number, expected):
    assert compact(number) == expected


def test_compact_non_string_raises():
    with pytest.raises((AttributeError, TypeError)):
        compact(None)
    with pytest.raises((AttributeError, TypeError)):
        compact(123)


@pytest.mark.parametrize(
    "number, expected",
    [
        ("BExx435411161155", "31"),
        ("BE00435411161155", "31"),
        ("BE31435411161155", "31"),
        ("GRxx0110105000001054 7023795", "16"),
        ("be xx 4354 1116 1155", "31"),
    ],
)
def test_calc_check_digits(number, expected):
    assert calc_check_digits(number) == expected


@pytest.mark.parametrize("number", VALID_IBANS)
def test_calc_check_digits_matches_existing(number):
    assert calc_check_digits(number) == number[2:4]


def test_calc_check_digits_ignores_supplied_digits():
    assert calc_check_digits("BE99435411161155") == calc_check_digits("BE00435411161155")


def test_calc_check_digits_invalid_character_raises():
    with pytest.raises(ValidationError):
        calc_check_digits("BExx4354!1161155")


@pytest.mark.parametrize(
    "structure, valid, invalid",
    [
        ("2n", ["12"], ["1", "123", "ab", ""]),
        ("3a", ["ABC"], ["abc", "AB", "ABCD", "AB1"]),
        ("3c", ["aB1", "abc", "ABC", "123"], ["ab", "abcd", "a-1"]),
        ("2n3a", ["12ABC"], ["1ABC", "12AB", "12abc"]),
        ("4a2n2c", ["ABCD12ab"], ["ABCD1ab", "abcd12ab"]),
        ("10n", ["0123456789"], ["012345678", "01234567890"]),
        ("1n", ["5"], ["", "55", "a"]),
    ],
)
def test_struct_to_re(structure, valid, invalid):
    pattern = _struct_to_re(structure)
    assert isinstance(pattern, re.Pattern)
    for value in valid:
        assert pattern.match(value)
    for value in invalid:
        assert not pattern.match(value)


def test_struct_to_re_anchored():
    pattern = _struct_to_re("2n")
    assert pattern.pattern.startswith("^")
    assert pattern.pattern.endswith("$")


def test_struct_to_re_empty_structure_matches_only_empty():
    pattern = _struct_to_re("")
    assert pattern.match("")
    assert not pattern.match("a")


def test_struct_to_re_ignores_unrecognised_parts():
    pattern = _struct_to_re("0n")
    assert pattern.pattern == "^0n$"


def test_struct_to_re_pattern_contents():
    assert _struct_to_re("2n3a1c").pattern == "^[0-9]{2}[A-Z]{3}[A-Za-z0-9]{1}$"


def test_struct_regex_does_not_match_zero_count():
    assert iban._struct_re.match("0!n") is None
    assert iban._struct_re.match("05!n") is None
    assert iban._struct_re.match("5!n") is not None
    assert iban._struct_re.match("5!x") is None


def test_get_cc_module_is_cached(monkeypatch):
    calls = []
    sentinel = object()

    def fake(cc, name):
        calls.append((cc, name))
        return sentinel

    monkeypatch.setattr(iban, "get_cc_module", fake)
    assert _get_cc_module("XX") is sentinel
    assert _get_cc_module("xx") is sentinel
    assert _get_cc_module("Xx") is sentinel
    assert calls == [("xx", "iban")]
    assert iban._country_modules == {"xx": sentinel}


def test_get_cc_module_caches_none(monkeypatch):
    calls = []

    def fake(cc, name):
        calls.append(cc)
        return None

    monkeypatch.setattr(iban, "get_cc_module", fake)
    assert _get_cc_module("yy") is None
    assert _get_cc_module("YY") is None
    assert calls == ["yy"]
    assert "yy" in iban._country_modules


def test_get_cc_module_separate_entries_per_country(monkeypatch):
    monkeypatch.setattr(iban, "get_cc_module", lambda cc, name: cc.upper())
    assert _get_cc_module("aa") == "AA"
    assert _get_cc_module("bb") == "BB"
    assert set(iban._country_modules) == {"aa", "bb"}


def test_get_cc_module_real_lookup():
    assert _get_cc_module("be") is not None
    assert _get_cc_module("zz") is None


@pytest.mark.parametrize("number", VALID_IBANS)
def test_validate_valid(number):
    assert validate(number) == number
    assert validate(number, check_country=False) == number


def test_validate_returns_compact_form():
    assert validate("GR16 0110 1050 0000 1054 7023 795") == "GR1601101050000010547023795"
    assert validate("be31 4354 1116 1155") == "BE31435411161155"
    assert validate("BE31-4354-1116-1155") == "BE31435411161155"
    assert validate(" BE31435411161155 ") == "BE31435411161155"


def test_validate_invalid_checksum():
    with pytest.raises(InvalidChecksum):
        validate("BE32435411161155")
    with pytest.raises(InvalidChecksum):
        validate("GR1701101050000010547023795")
    with pytest.raises(InvalidChecksum):
        validate("DE89370400440532013001")


def test_validate_invalid_checksum_also_without_country_check():
    with pytest.raises(InvalidChecksum):
        validate("BE32435411161155", check_country=False)


@pytest.mark.parametrize("number", ["", "   ", "1", "ABC"])
def test_validate_garbage_raises_validation_error(number):
    with pytest.raises(ValidationError):
        validate(number)


def test_validate_non_alphanumeric_raises_validation_error():
    with pytest.raises(ValidationError):
        validate("BE31!35411161155")


def test_validate_non_string_raises():
    with pytest.raises((AttributeError, TypeError)):
        validate(None)
    with pytest.raises((AttributeError, TypeError)):
        validate(12345)


def _make_valid(country, bban):
    check = calc_check_digits(country + "00" + bban)
    return country + check + bban


def test_validate_unknown_country_raises_invalid_component():
    number = _make_valid("XX", "123456789")
    with pytest.raises(InvalidComponent):
        validate(number)
    with pytest.raises(InvalidComponent):
        validate(number, check_country=False)


def test_validate_wrong_bban_structure_raises_invalid_format():
    number = _make_valid("BE", "43541116115A")
    with pytest.raises(InvalidFormat):
        validate(number)
    with pytest.raises(InvalidFormat):
        validate(number, check_country=False)


def test_validate_wrong_bban_length_raises_invalid_format():
    number = _make_valid("BE", "4354111611555")
    with pytest.raises(InvalidFormat):
        validate(number)


def test_validate_lowercase_bban_letters_in_alpha_field():
    number = _make_valid("GB", "nwbk60161331926819".upper())
    assert validate(number) == number
    assert validate(number.lower()) == number


def test_validate_country_module_called(monkeypatch):
    module = _FakeModule()
    monkeypatch.setattr(iban, "_get_cc_module", lambda cc: module)
    assert validate("BE31435411161155") == "BE31435411161155"
    assert module.calls == ["BE31435411161155"]


def test_validate_country_module_receives_country_code(monkeypatch):
    seen = []
    module = _FakeModule()

    def fake(cc):
        seen.append(cc)
        return module

    monkeypatch.setattr(iban, "_get_cc_module", fake)
    validate("be31 4354 1116 1155")
    assert seen == ["BE"]


def test_validate_country_module_error_propagates(monkeypatch):
    module = _FakeModule(error=InvalidChecksum())
    monkeypatch.setattr(iban, "_get_cc_module", lambda cc: module)
    with pytest.raises(InvalidChecksum):
        validate("BE31435411161155")
    assert module.calls == ["BE31435411161155"]


def test_validate_country_module_skipped_when_disabled(monkeypatch):
    def boom(cc):
        raise AssertionError("must not be called")

    monkeypatch.setattr(iban, "_get_cc_module", boom)
    assert validate("BE31435411161155", check_country=False) == "BE31435411161155"


def test_validate_country_module_none_is_accepted(monkeypatch):
    monkeypatch.setattr(iban, "_get_cc_module", lambda cc: None)
    assert validate("BE31435411161155") == "BE31435411161155"


def test_validate_country_module_not_called_for_bad_checksum(monkeypatch):
    module = _FakeModule()
    monkeypatch.setattr(iban, "_get_cc_module", lambda cc: module)
    with pytest.raises(InvalidChecksum):
        validate("BE32435411161155")
    assert module.calls == []


def test_validate_country_module_not_called_for_bad_structure(monkeypatch):
    module = _FakeModule()
    monkeypatch.setattr(iban, "_get_cc_module", lambda cc: module)
    number = _make_valid("BE", "43541116115A")
    with pytest.raises(InvalidFormat):
        validate(number)
    assert module.calls == []


def test_validate_missing_bban_key_uses_empty_structure(monkeypatch):
    class FakeDb:
        def info(self, number):
            return [(number[:2], {"country": "Fake"})]

    monkeypatch.setattr(iban, "_ibandb", FakeDb())
    number = _make_valid("BE", "")
    with pytest.raises(InvalidFormat):
        validate(number, check_country=False)


def test_validate_empty_info_raises_invalid_component(monkeypatch):
    class FakeDb:
        def info(self, number):
            return [(number[:2], None)]

    monkeypatch.setattr(iban, "_ibandb", FakeDb())
    with pytest.raises(InvalidComponent):
        validate("BE31435411161155")


def test_validate_empty_dict_info_raises_invalid_component(monkeypatch):
    class FakeDb:
        def info(self, number):
            return [(number[:2], {})]

    monkeypatch.setattr(iban, "_ibandb", FakeDb())
    with pytest.raises(InvalidComponent):
        validate("BE31435411161155")


def test_validate_uses_bban_structure_from_database(monkeypatch):
    class FakeDb:
        def info(self, number):
            return [(number[:2], {"bban": "12!n"})]

    monkeypatch.setattr(iban, "_ibandb", FakeDb())
    assert validate("BE31435411161155", check_country=False) == "BE31435411161155"
    number = _make_valid("BE", "12345678901A")
    with pytest.raises(InvalidFormat):
        validate(number, check_country=False)


@pytest.mark.parametrize("number", VALID_IBANS)
def test_is_valid_true(number):
    assert is_valid(number) is True
    assert is_valid(number, check_country=False) is True
    assert is_valid(number.lower()) is True


def test_is_valid_formatted_input():
    assert is_valid("GR16 0110 1050 0000 1054 7023 795") is True
    assert is_valid("BE31-4354-1116-1155") is True


@pytest.mark.parametrize(
    "number",
    [
        "BE32435411161155",
        "",
        "   ",
        "ABC",
        "1",
        "BE31!35411161155",
        _make_valid("XX", "123456789"),
        _make_valid("BE", "43541116115A"),
    ],
)
def test_is_valid_false(number):
    assert is_valid(number) is False
    assert is_valid(number, check_country=False) is False


def test_is_valid_country_module_failure(monkeypatch):
    module = _FakeModule(error=InvalidComponent())
    monkeypatch.setattr(iban, "_get_cc_module", lambda cc: module)
    assert is_valid("BE31435411161155") is False
    assert is_valid("BE31435411161155", check_country=False) is True


def test_is_valid_non_validation_errors_propagate():
    with pytest.raises((AttributeError, TypeError)):
        is_valid(None)


def test_is_valid_returns_bool_for_each_exception_type(monkeypatch):
    for error in (InvalidChecksum(), InvalidFormat(), InvalidLength(), InvalidComponent()):
        module = _FakeModule(error=error)
        monkeypatch.setattr(iban, "_get_cc_module", lambda cc, m=module: m)
        assert is_valid("BE31435411161155") is False


@pytest.mark.parametrize(
    "number, expected",
    [
        ("GR1601101050000010547023795", "GR16 0110 1050 0000 1054 7023 795"),
        ("BE31435411161155", "BE31 4354 1116 1155"),
        ("be31 4354 1116 1155", "BE31 4354 1116 1155"),
        ("BE31-4354-1116-1155", "BE31 4354 1116 1155"),
        ("ABCD", "ABCD"),
        ("ABCDE", "ABCD E"),
        ("A", "A"),
        ("", ""),
        ("   ", ""),
    ],
)
def test_format_default_separator(number, expected):
    assert format(number) == expected


@pytest.mark.parametrize(
    "separator, expected",
    [
        ("-", "BE31-4354-1116-1155"),
        ("", "BE31435411161155"),
        (".", "BE31.4354.1116.1155"),
        ("  ", "BE31  4354  1116  1155"),
    ],
)
def test_format_custom_separator(separator, expected):
    assert format("BE31435411161155", separator) == expected
    assert format("BE31435411161155", separator=separator) == expected


@pytest.mark.parametrize("number", VALID_IBANS)
def test_format_compact_roundtrip(number):
    assert compact(format(number)) == number
    assert format(number).replace(" ", "") == number


def test_format_groups_of_four():
    formatted = format("GR1601101050000010547023795")
    groups = formatted.split(" ")
    assert all(len(g) == 4 for g in groups[:-1])
    assert 1 <= len(groups[-1]) <= 4


def test_format_non_string_raises():
    with pytest.raises((AttributeError, TypeError)):
        format(None)


def test_format_invalid_separator_type_raises():
    with pytest.raises(AttributeError):
        format("BE31435411161155", None)
    with pytest.raises(TypeError):
        format("BE31435411161155", 5)


def test_module_docstring_examples():
    assert validate("GR16 0110 1050 0000 1054 7023 795") == "GR1601101050000010547023795"
    assert validate("BE31435411161155") == "BE31435411161155"
    assert compact("GR16 0110 1050 0000 1054 7023 795") == "GR1601101050000010547023795"
    assert format("GR1601101050000010547023795") == "GR16 0110 1050 0000 1054 7023 795"
    assert calc_check_digits("BExx435411161155") == "31"


def test_module_level_state():
    assert iban._ibandb is not None
    assert isinstance(iban._country_modules, dict)
    assert iban._struct_re.pattern == r"([1-9][0-9]*)!([nac])"