import pytest
from itsdangerous import encoding

def test_want_bytes_with_bytes():
    assert encoding.want_bytes(b"hello") == b"hello"

def test_want_bytes_with_str():
    assert encoding.want_bytes("hello") == b"hello"

def test_want_bytes_with_encoding_errors():
    assert encoding.want_bytes("héllo", encoding="latin-1") == b"h\xe9llo"

def test_base64_encode_bytes():
    assert encoding.base64_encode(b"hello world") == b"aGVsbG8gd29ybGQ"

def test_base64_encode_str():
    assert encoding.base64_encode("hello world") == b"aGVsbG8gd29ybGQ"

def test_base64_encode_padding_stripped():
    assert encoding.base64_encode(b"f") == b"Zg"

def test_base64_decode_bytes():
    assert encoding.base64_decode(b"aGVsbG8gd29ybGQ") == b"hello world"

def test_base64_decode_str():
    assert encoding.base64_decode("aGVsbG8gd29ybGQ") == b"hello world"

def test_base64_decode_with_padding():
    assert encoding.base64_decode(b"Zg==") == b"f"

def test_base64_decode_invalid_data():
    with pytest.raises(encoding.BadData) as exc_info:
        encoding.base64_decode("invalid_base64!@#")
    assert "Invalid base64-encoded data" in str(exc_info.value)

def test_int_to_bytes_zero():
    assert encoding.int_to_bytes(0) == b""

def test_int_to_bytes_positive():
    assert encoding.int_to_bytes(1) == b"\x01"
    assert encoding.int_to_bytes(256) == b"\x01\x00"

def test_bytes_to_int_empty():
    assert encoding.bytes_to_int(b"") == 0

def test_bytes_to_int_positive():
    assert encoding.bytes_to_int(b"\x01") == 1
    assert encoding.bytes_to_int(b"\x01\x00") == 256

def test_int_bytes_roundtrip():
    numbers = [0, 1, 127, 128, 255, 256, 65535, 2**32 - 1, 2**64 - 1]
    for num in numbers:
        assert encoding.bytes_to_int(encoding.int_to_bytes(num)) == num