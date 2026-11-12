import pytest
from stdnum.exceptions import InvalidComponent, InvalidFormat, InvalidChecksum, InvalidLength
from stdnum.iban import (
    compact,
    calc_check_digits,
    _struct_to_re,
    _get_cc_module,
    validate,
    is_valid,
    format,
)

def test_compact():
    assert compact("GR16 0110 1050 0000 1054 7023 795") == "GR1601101050000010547023795"
    assert compact("  be31-4354-1116-1155  ") == "BE31435411161155"

def test_calc_check_digits():
    assert calc_check_digits("BExx435411161155") == "31"
    assert calc_check_digits("grxx01101050000010547023795") == "16"

def test_struct_to_re():
    pattern = _struct_to_re("4n2a5c")
    assert pattern.match("1234AB12345")
    assert not pattern.match("1234AB123456")
    assert not pattern.match("1234ab12345")

def test_get_cc_module():
    mod = _get_cc_module("be")
    assert mod is not None
    assert _get_cc_module("BE") is mod
    assert _get_cc_module("xx") is None

def test_validate_valid():
    valid_iban = "GR1601101050000010547023795"
    assert validate(valid_iban) == valid_iban
    assert validate("BE31435411161155") == "BE31435411161155"

def test_validate_invalid_checksum():
    with pytest.raises(ValidationError):
        validate("GR1501101050000010547023795")

def test_validate_invalid_length():
    with pytest.raises(ValidationError):
        validate("GR1601101050000010547023")

def test_validate_invalid_format():
    with pytest.raises(ValidationError):
        validate("GR16ZZZZ1050000010547023795")

def test_validate_unknown_country():
    with pytest.raises(ValidationError):
        validate("XX1601101050000010547023795")

def test_validate_check_country_false():
    invalid_cc_iban = "XX1601101050000010547023795"
    with pytest.raises(ValidationError):
        validate(invalid_cc_iban, check_country=True)
    with pytest.raises(InvalidComponent):
        validate(invalid_cc_iban, check_country=False)

def test_is_valid():
    assert is_valid("GR1601101050000010547023795") is True
    assert is_valid("GR1501101050000010547023795") is False

def test_format():
    assert format("GR1601101050000010547023795") == "GR16 0110 1050 0000 1054 7023 795"
    assert format("BE31435411161155", separator="-") == "BE31-4354-1116-1155"