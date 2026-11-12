
import hashlib
import pytest

from base58 import (
    __version__,
    BITCOIN_ALPHABET,
    RIPPLE_ALPHABET,
    XRP_ALPHABET,
    alphabet,
    scrub_input,
    b58encode_int,
    b58decode_int,
    b58encode,
    b58decode,
    b58encode_check,
    b58decode_check,
    _get_base58_decode_map,
)


@pytest.fixture(autouse=True)
def clear_decode_cache():
    _get_base58_decode_map.cache_clear()
    yield
    _get_base58_decode_map.cache_clear()


@pytest.fixture
def sample_data():
    return b"Hello, Bitcoin!"


def test_version():
    assert __version__ == "2.1.1"


def test_alphabet_constants():
    assert BITCOIN_ALPHABET == b"123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    assert RIPPLE_ALPHABET == b"rpshnaf39wBUDNEGHJKLM4PQRST7VWXYZ2bcdeCg65jkm8oFqi1tuvAxyz"
    assert XRP_ALPHABET == RIPPLE_ALPHABET
    assert alphabet == BITCOIN_ALPHABET
    assert len(BITCOIN_ALPHABET) == 58
    assert len(RIPPLE_ALPHABET) == 58


def test_scrub_input_bytes():
    value = b"hello"
    assert scrub_input(value) is value


def test_scrub_input_string():
    assert scrub_input("hello") == b"hello"


def test_scrub_input_non_ascii_string():
    with pytest.raises(UnicodeEncodeError):
        scrub_input("你好")


@pytest.mark.parametrize(
    "value, expected",
    [
        (0, b"1"),
        (1, b"2"),
        (57, b"z"),
        (58, b"21"),
        (59, b"22"),
        (100, b"2j"),
        (255, b"5Q"),
        (256, b"5R"),
        (123456789, b"BukQL"),
    ],
)
def test_b58encode_int(value, expected):
    assert b58encode_int(value) == expected


def test_b58encode_int_zero_default_one():
    assert b58encode_int(0) == b"1"


def test_b58encode_int_zero_without_default_one():
    assert b58encode_int(0, default_one=False) == b""


def test_b58encode_int_custom_alphabet():
    custom = b"0123456789"
    assert b58encode_int(123, alphabet=custom) == b"123"


def test_b58encode_int_negative():
    with pytest.raises(ValueError):
        b58encode_int(-1)


def test_b58encode_int_empty_alphabet():
    with pytest.raises(ZeroDivisionError):
        b58encode_int(1, alphabet=b"")


@pytest.mark.parametrize(
    "value",
    [
        b"",
        b"\x00",
        b"\x00\x00",
        b"\x01",
        b"\xff",
        b"hello",
        b"\x00hello",
        b"\x00\x00hello",
        b"\xff\xff\xff\xff",
    ],
)
def test_b58encode_decode_roundtrip(value):
    encoded = b58encode(value)
    assert isinstance(encoded, bytes)
    assert b58decode(encoded) == value


def test_b58encode_string():
    assert b58encode("hello") == b58encode(b"hello")


def test_b58encode_empty():
    assert b58encode(b"") == b""


def test_b58encode_leading_zeroes():
    assert b58encode(b"\x00\x00\x01") == b"112"
    assert b58decode(b"112") == b"\x00\x00\x01"


def test_b58encode_all_zeroes():
    assert b58encode(b"\x00\x00\x00") == b"111"
    assert b58decode(b"111") == b"\x00\x00\x00"


def test_b58encode_custom_alphabet():
    custom = b"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    value = b"hello"
    assert b58decode(b58encode(value, alphabet=custom), alphabet=custom) == value


def test_b58encode_non_ascii_string():
    with pytest.raises(UnicodeEncodeError):
        b58encode("你好")


@pytest.mark.parametrize(
    "value, expected",
    [
        (b"", 0),
        (b"1", 0),
        (b"2", 1),
        (b"z", 57),
        (b"21", 58),
        (b"22", 59),
        (b"5R", 256),
    ],
)
def test_b58decode_int(value, expected):
    assert b58decode_int(value) == expected


def test_b58decode_int_string():
    assert b58decode_int("2") == 1


def test_b58decode_int_trailing_whitespace():
    assert b58decode_int(b"2 \n\t") == 1


def test_b58decode_int_leading_whitespace():
    with pytest.raises(ValueError, match="Invalid character"):
        b58decode_int(b" 2")


def test_b58decode_int_invalid_character():
    with pytest.raises(ValueError, match="Invalid character"):
        b58decode_int(b"0")


def test_b58decode_int_invalid_character_message():
    with pytest.raises(ValueError) as exc:
        b58decode_int(b"0")
    assert str(exc.value) == "Invalid character '0'"


def test_b58decode_int_non_ascii_invalid_byte():
    with pytest.raises(ValueError, match="Invalid character"):
        b58decode_int(b"\xff")


def test_b58decode_int_custom_alphabet():
    custom = b"0123456789"
    assert b58decode_int(b"123", alphabet=custom) == 123


def test_b58decode_int_alphabet_containing_space():
    custom = b" 123456789"
    assert b58decode_int(b"1 ", alphabet=custom) == 2


def test_b58decode_int_empty_alphabet():
    with pytest.raises(ZeroDivisionError):
        b58decode_int(b"1", alphabet=b"")


def test_b58decode_int_duplicate_alphabet():
    custom = b"112"
    assert b58decode_int(b"2", alphabet=custom) == 2


def test_b58decode_int_autofix_zero():
    assert b58decode_int(b"0", autofix=True) == 0


def test_b58decode_int_autofix_uppercase_o():
    assert b58decode_int(b"O", autofix=True) == 0


def test_b58decode_int_autofix_lowercase_o():
    assert b58decode_int(b"o", autofix=True) == 0


def test_b58decode_int_autofix_uppercase_i():
    assert b58decode_int(b"I", autofix=True) == 0


def test_b58decode_int_autofix_lowercase_l():
    assert b58decode_int(b"l", autofix=True) == 0


def test_b58decode_int_autofix_disabled():
    with pytest.raises(ValueError):
        b58decode_int(b"0", autofix=False)


def test_b58decode_int_autofix_ambiguous_group():
    custom = b"01"
    result = _get_base58_decode_map(custom, True)
    assert result[ord("0")] == 0
    assert result[ord("O")] == 0
    assert result[ord("o")] == 0


def test_b58decode_int_autofix_without_unique_pivot():
    custom = b"01OI"
    result = _get_base58_decode_map(custom, True)
    assert result[ord("0")] == 0
    assert result[ord("O")] == 2
    assert result[ord("I")] == 3


def test_decode_map_cache():
    first = _get_base58_decode_map(BITCOIN_ALPHABET, False)
    second = _get_base58_decode_map(BITCOIN_ALPHABET, False)
    assert first is second
    assert _get_base58_decode_map.cache_info().hits >= 1


def test_b58decode_empty():
    assert b58decode(b"") == b""


def test_b58decode_single_zero():
    assert b58decode(b"1") == b"\x00"


def test_b58decode_multiple_zeroes():
    assert b58decode(b"1111") == b"\x00\x00\x00\x00"


def test_b58decode_integer_value():
    assert b58decode(b"2") == b"\x01"


def test_b58decode_trailing_whitespace():
    assert b58decode(b"2 \n\t") == b"\x01"


def test_b58decode_leading_whitespace():
    with pytest.raises(ValueError):
        b58decode(b" 2")


def test_b58decode_invalid_character():
    with pytest.raises(ValueError):
        b58decode(b"0")


def test_b58decode_string():
    assert b58decode("2") == b"\x01"


def test_b58decode_custom_alphabet():
    custom = b"0123456789"
    assert b58decode(b"123", alphabet=custom) == bytes([123])


def test_b58decode_custom_alphabet_with_leading_zero():
    custom = b"0123456789"
    assert b58decode(b"001", alphabet=custom) == b"\x00\x00\x01"


def test_b58decode_autofix():
    assert b58decode(b"O", autofix=True) == b""


def test_b58decode_autofix_leading_zero():
    assert b58decode(b"0", autofix=True) == b"\x00"


def test_b58decode_non_ascii_string():
    with pytest.raises(UnicodeEncodeError):
        b58decode("你好")


def test_b58encode_ripple_alphabet():
    value = b"Ripple"
    encoded = b58encode(value, alphabet=RIPPLE_ALPHABET)
    assert b58decode(encoded, alphabet=RIPPLE_ALPHABET) == value


@pytest.mark.parametrize(
    "value",
    [
        b"",
        b"\x00",
        b"\x00\x00",
        b"hello",
        b"Bitcoin",
        b"\x00Bitcoin",
        bytes(range(256)),
    ],
)
def test_b58encode_check_decode_check_roundtrip(value):
    encoded = b58encode_check(value)
    assert isinstance(encoded, bytes)
    assert b58decode_check(encoded) == value


def test_b58encode_check_string():
    assert b58encode_check("hello") == b58encode_check(b"hello")


def test_b58encode_check_empty():
    encoded = b58encode_check(b"")
    assert b58decode_check(encoded) == b""


def test_b58encode_check_custom_alphabet():
    custom = b"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    value = b"test data"
    encoded = b58encode_check(value, alphabet=custom)
    assert b58decode_check(encoded, alphabet=custom) == value


def test_b58encode_check_ripple_alphabet():
    value = b"Ripple test"
    encoded = b58encode_check(value, alphabet=RIPPLE_ALPHABET)
    assert b58decode_check(encoded, alphabet=RIPPLE_ALPHABET) == value


def test_b58encode_check_non_ascii_string():
    with pytest.raises(UnicodeEncodeError):
        b58encode_check("你好")


def test_b58decode_check_invalid_checksum():
    encoded = bytearray(b58encode_check(b"hello"))
    encoded[-1] = ord("2") if encoded[-1] != ord("2") else ord("3")
    with pytest.raises(ValueError, match="Invalid checksum"):
        b58decode_check(bytes(encoded))


def test_b58decode_check_empty_input():
    with pytest.raises(ValueError, match="Invalid checksum"):
        b58decode_check(b"")


def test_b58decode_check_too_short():
    encoded = b58encode(b"abc")
    with pytest.raises(ValueError, match="Invalid checksum"):
        b58decode_check(encoded)


def test_b58decode_check_invalid_base58_character():
    with pytest.raises(ValueError, match="Invalid character"):
        b58decode_check(b"0")


def test_b58decode_check_string():
    encoded = b58encode_check("hello").decode("ascii")
    assert b58decode_check(encoded) == b"hello"


def test_b58decode_check_autofix():
    encoded = b58encode_check(b"hello")
    assert b58decode_check(encoded, autofix=True) == b"hello"


def test_b58decode_check_non_ascii_string():
    with pytest.raises(UnicodeEncodeError):
        b58decode_check("你好")


def test_checksum_matches_double_sha256():
    value = b"Bitcoin"
    encoded = b58encode_check(value)
    decoded = b58decode(encoded)
    digest = hashlib.sha256(hashlib.sha256(value).digest()).digest()
    assert decoded == value + digest[:4]


def test_large_integer_encoding():
    value = 2**1024
    encoded = b58encode_int(value)
    assert b58decode_int(encoded) == value


def test_large_byte_sequence_roundtrip():
    value = bytes(range(256)) * 10
    assert b58decode(b58encode(value)) == value


@pytest.mark.parametrize(
    "value",
    [
        b"\x00",
        b"\x00\x00\x00",
        b"\x01",
        b"\xff",
        b"\x00\xff",
        bytes(range(32)),
        bytes(range(64)),
    ],
)
def test_roundtrip_with_ripple_alphabet(value):
    assert b58decode(
        b58encode(value, alphabet=RIPPLE_ALPHABET),
        alphabet=RIPPLE_ALPHABET,
    ) == value


def test_b58decode_int_bytes_with_all_valid_characters():
    encoded = BITCOIN_ALPHABET
    decoded = b58decode_int(encoded)
    assert decoded >= 0


def test_b58decode_int_preserves_exception_cause():
    with pytest.raises(ValueError) as exc:
        b58decode_int(b"0")
    assert exc.value.__cause__ is None


def test_b58decode_int_whitespace_alphabet_behavior():
    custom = b" 123456789"
    assert b58decode_int(b"1", alphabet=custom) == 2


def test_b58decode_check_checksum_mutation():
    original = b"original payload"
    encoded = b58encode_check(original)
    decoded = bytearray(b58decode(encoded))
    decoded[0] ^= 1
    modified = b58encode(bytes(decoded))
    with pytest.raises(ValueError, match="Invalid checksum"):
        b58decode_check(modified)
