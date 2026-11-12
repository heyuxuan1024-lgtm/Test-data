import pytest
import base58

def test_scrub_input():
    assert base58.scrub_input("test") == b"test"
    assert base58.scrub_input(b"test") == b"test"

def test_b58encode_int():
    assert base58.b58encode_int(0, default_one=True) == b"1"
    assert base58.b58encode_int(0, default_one=False) == b""
    assert base58.b58encode_int(57, default_one=True, alphabet=b"1234") == b"21"

def test_b58encode():
    assert base58.b58encode(b"hello") == b"CNkxxF"
    assert base58.b58encode("hello") == b"CNkxxF"
    assert base58.b58encode(b"\0\0hello") == b"11CNkxxF"
    assert base58.b58encode(b"hello", alphabet=base58.RIPPLE_ALPHABET) == b"cnmGGd"

def test_b58decode_int():
    assert base58.b58decode_int(b"1") == 0
    assert base58.b58decode_int(b"21", alphabet=b"1234") == 57
    with pytest.raises(ValueError, match="Invalid character"):
        base58.b58decode_int(b"INVALID")

def test_b58decode_int_autofix():
    assert base58.b58decode_int(b"0", autofix=True) == 0
    assert base58.b58decode_int(b"O", autofix=True) == 0
    assert base58.b58decode_int(b"o", autofix=True) == 0
    assert base58.b58decode_int(b"I", autofix=True) == 32
    assert base58.b58decode_int(b"l", autofix=True) == 32
    assert base58.b58decode_int(b"1", autofix=True) == 0

def test_b58decode():
    assert base58.b58decode(b"CNkxxF") == b"hello"
    assert base58.b58decode("CNkxxF") == b"hello"
    assert base58.b58decode(b"11CNkxxF") == b"\0\0hello"
    assert base58.b58decode(b"CNkxxF   \n") == b"hello"

def test_b58encode_check():
    encoded = base58.b58encode_check(b"hello")
    assert isinstance(encoded, bytes)
    assert len(encoded) > 4

def test_b58decode_check():
    encoded = base58.b58encode_check(b"hello")
    decoded = base58.b58decode_check(encoded)
    assert decoded == b"hello"

def test_b58decode_check_invalid():
    encoded = bytearray(base58.b58encode_check(b"hello"))
    encoded[-1] ^= 0x01
    with pytest.raises(ValueError, match="Invalid checksum"):
        base58.b58decode_check(bytes(encoded))

def test_alphabet_with_space():
    space_alphabet = b" 123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    encoded = base58.b58encode(b"test", alphabet=space_alphabet)
    decoded = base58.b58decode(encoded, alphabet=space_alphabet)
    assert decoded == b"test"