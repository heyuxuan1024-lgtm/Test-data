import pytest
from base58 import (
    scrub_input,
    b58encode_int,
    b58encode,
    b58decode_int,
    b58decode,
    b58encode_check,
    b58decode_check,
    BITCOIN_ALPHABET,
    RIPPLE_ALPHABET,
)

def test_scrub_input():
    assert scrub_input("test") == b"test"
    assert scrub_input(b"test") == b"test"

def test_b58encode_int():
    assert b58encode_int(0, default_one=True) == b"1"
    assert b58encode_int(0, default_one=False) == b""
    assert b58encode_int(57, default_one=True, alphabet=b"1234") == b"21"

def test_b58encode():
    assert b58encode(b"hello") == b"CNkxxF"
    assert b58encode("hello") == b"CNkxxF"
    assert b58encode(b"\0\0hello") == b"11CNkxxF"
    assert b58encode(b"hello", alphabet=RIPPLE_ALPHABET) == b"cnmGGd"

def test_b58decode_int():
    assert b58decode_int(b"1") == 0
    assert b58decode_int(b"21", alphabet=b"1234") == 57
    with pytest.raises(ValueError, match="Invalid character"):
        b58decode_int(b"INVALID")

def test_b58decode_int_autofix():
    assert b58decode_int(b"0", autofix=True) == 0
    assert b58decode_int(b"O", autofix=True) == 0
    assert b58decode_int(b"o", autofix=True) == 0
    assert b58decode_int(b"I", autofix=True) == 32
    assert b58decode_int(b"l", autofix=True) == 32
    assert b58decode_int(b"1", autofix=True) == 0
    assert b58decode_int(b"0", autofix=True) == 0

def test_b58decode():
    assert b58decode(b"CNkxxF") == b"hello"
    assert b58decode("CNkxxF") == b"hello"
    assert b58decode(b"11CNkxxF") == b"\0\0hello"
    assert b58decode(b"CNkxxF   \n") == b"hello"

def test_b58encode_check():
    encoded = b58encode_check(b"hello")
    assert isinstance(encoded, bytes)
    assert len(encoded) > 4

def test_b58decode_check():
    encoded = b58encode_check(b"hello")
    decoded = b58decode_check(encoded)
    assert decoded == b"hello"

def test_b58decode_check_invalid():
    encoded = bytearray(b58encode_check(b"hello"))
    encoded[-1] ^= 0x01
    with pytest.raises(ValueError, match="Invalid checksum"):
        b58decode_check(bytes(encoded))

def test_alphabet_with_space():
    space_alphabet = b" 123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    encoded = b58encode(b"test", alphabet=space_alphabet)
    decoded = b58decode(encoded, alphabet=space_alphabet)
    assert decoded == b"test"