
import base64
import struct

import pytest

from itsdangerous import encoding


def test_want_bytes_with_string():
    assert encoding.want_bytes("hello") == b"hello"


def test_want_bytes_with_unicode():
    assert encoding.want_bytes("你好") == "你好".encode("utf-8")


def test_want_bytes_with_custom_encoding():
    assert encoding.want_bytes("café", encoding="latin-1") == b"caf\xe9"


def test_want_bytes_with_ignore_errors():
    assert encoding.want_bytes("café", encoding="ascii", errors="ignore") == b"caf"


def test_want_bytes_with_replace_errors():
    assert encoding.want_bytes("café", encoding="ascii", errors="replace") == b"caf?"


def test_want_bytes_with_bytes():
    value = b"\x00\xffhello"
    assert encoding.want_bytes(value) is value


@pytest.mark.parametrize("value", [b"", b"data", bytearray(b"data"), None, 123])
def test_want_bytes_returns_non_string_unchanged(value):
    result = encoding.want_bytes(value)
    assert result is value


def test_want_bytes_invalid_encoding():
    with pytest.raises(LookupError):
        encoding.want_bytes("hello", encoding="not-a-real-encoding")


def test_want_bytes_encoding_error():
    with pytest.raises(UnicodeEncodeError):
        encoding.want_bytes("你好", encoding="ascii")


def test_base64_encode_empty_bytes():
    assert encoding.base64_encode(b"") == b""


def test_base64_encode_empty_string():
    assert encoding.base64_encode("") == b""


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("hello", b"aGVsbG8"),
        (b"hello", b"aGVsbG8"),
        ("你好", "你好".encode("utf-8")),
        (b"\xfb\xff", b"-_8"),
        (b"\x00\x00", b"AAA"),
    ],
)
def test_base64_encode(value, expected):
    if isinstance(value, str) and value == "你好":
        expected = base64.urlsafe_b64encode(value.encode("utf-8")).rstrip(b"=")
    assert encoding.base64_encode(value) == expected


def test_base64_encode_output_has_no_padding():
    result = encoding.base64_encode(b"f")
    assert result == b"Zg"
    assert b"=" not in result


def test_base64_encode_url_safe_characters():
    result = encoding.base64_encode(b"\xfb\xff")
    assert result == b"-_8"
    assert b"+" not in result
    assert b"/" not in result
    assert b"=" not in result


def test_base64_encode_bytearray():
    assert encoding.base64_encode(bytearray(b"hello")) == b"aGVsbG8"


def test_base64_encode_non_ascii_string():
    assert encoding.base64_encode("café") == base64.urlsafe_b64encode(
        "café".encode("utf-8")
    ).rstrip(b"=")


def test_base64_decode_empty_bytes():
    assert encoding.base64_decode(b"") == b""


def test_base64_decode_empty_string():
    assert encoding.base64_decode("") == b""


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (b"aGVsbG8", b"hello"),
        ("aGVsbG8", b"hello"),
        (b"Zg", b"f"),
        (b"Zm8", b"fo"),
        (b"Zm9v", b"foo"),
        (b"-_8", b"\xfb\xff"),
        (b"AA", b"\x00"),
        (b"AAA", b"\x00\x00"),
        (b"AAAA", b"\x00\x00\x00"),
    ],
)
def test_base64_decode(value, expected):
    assert encoding.base64_decode(value) == expected


def test_base64_decode_with_existing_padding():
    assert encoding.base64_decode(b"aGVsbG8=") == b"hello"
    assert encoding.base64_decode(b"aGVsbG8===") == b"hello"


def test_base64_decode_adds_padding():
    assert encoding.base64_decode(b"Zg") == b"f"
    assert encoding.base64_decode(b"Zm8") == b"fo"


def test_base64_decode_url_safe_characters():
    assert encoding.base64_decode(b"-_8") == b"\xfb\xff"


def test_base64_decode_ignores_non_ascii_bytes():
    assert encoding.base64_decode(b"aGVs\xffbG8") == b"hello"


def test_base64_decode_ignores_non_ascii_text():
    assert encoding.base64_decode("aGVs\u2603bG8") == b"hello"


def test_base64_decode_ignores_invalid_ascii_characters():
    assert encoding.base64_decode(b"aGVs!bG8") == b"hello"


def test_base64_decode_invalid_data_raises_bad_data():
    with pytest.raises(encoding.BadData, match="Invalid base64-encoded data"):
        encoding.base64_decode(b"a===")


def test_base64_decode_invalid_data_preserves_cause():
    with pytest.raises(encoding.BadData) as exc_info:
        encoding.base64_decode(b"a===")
    assert isinstance(exc_info.value.__cause__, ValueError)


def test_base64_decode_non_string_non_bytes_type():
    with pytest.raises(TypeError):
        encoding.base64_decode(123)


def test_base64_decode_none():
    with pytest.raises(TypeError):
        encoding.base64_decode(None)


def test_base64_alphabet():
    assert encoding._base64_alphabet == (
        b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_="
    )


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (0, b""),
        (1, b"\x01"),
        (255, b"\xff"),
        (256, b"\x01\x00"),
        (65535, b"\xff\xff"),
        (65536, b"\x01\x00\x00"),
        (2**32, b"\x01\x00\x00\x00\x00"),
        (2**64 - 1, b"\xff" * 8),
    ],
)
def test_int_to_bytes(value, expected):
    assert encoding.int_to_bytes(value) == expected


def test_int_to_bytes_zero():
    assert encoding.int_to_bytes(0) == b""


def test_int_to_bytes_strips_leading_zero_bytes():
    assert encoding.int_to_bytes(0x00000102) == b"\x01\x02"


def test_int_to_bytes_boolean():
    assert encoding.int_to_bytes(True) == b"\x01"
    assert encoding.int_to_bytes(False) == b""


@pytest.mark.parametrize("value", [-1, -100, -(2**63)])
def test_int_to_bytes_negative_values_raise(value):
    with pytest.raises(struct.error):
        encoding.int_to_bytes(value)


def test_int_to_bytes_value_too_large():
    with pytest.raises(struct.error):
        encoding.int_to_bytes(2**64)


@pytest.mark.parametrize("value", ["1", 1.5, None, b"\x01"])
def test_int_to_bytes_invalid_types(value):
    with pytest.raises((struct.error, TypeError)):
        encoding.int_to_bytes(value)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (b"", 0),
        (b"\x00", 0),
        (b"\x01", 1),
        (b"\xff", 255),
        (b"\x01\x00", 256),
        (b"\xff\xff", 65535),
        (b"\x01\x00\x00", 65536),
        (b"\x01\x00\x00\x00\x00", 2**32),
        (b"\xff" * 8, 2**64 - 1),
    ],
)
def test_bytes_to_int(value, expected):
    assert encoding.bytes_to_int(value) == expected


def test_bytes_to_int_eight_bytes():
    value = b"\x01\x02\x03\x04\x05\x06\x07\x08"
    assert encoding.bytes_to_int(value) == 0x0102030405060708


def test_bytes_to_int_short_input_is_left_padded():
    assert encoding.bytes_to_int(b"\x01\x02") == 258
    assert encoding.bytes_to_int(b"\x00\x01") == 1


def test_bytes_to_int_empty_input():
    assert encoding.bytes_to_int(b"") == 0


def test_bytes_to_int_long_input_raises():
    with pytest.raises(struct.error):
        encoding.bytes_to_int(b"\x00" * 9)


def test_bytes_to_int_long_input_with_nonzero_prefix_raises():
    with pytest.raises(struct.error):
        encoding.bytes_to_int(b"\x01" + b"\x00" * 8)


def test_bytes_to_int_bytearray():
    assert encoding.bytes_to_int(bytearray(b"\x01\x02")) == 258


@pytest.mark.parametrize("value", [None, 123, "123", 1.5])
def test_bytes_to_int_invalid_types(value):
    with pytest.raises((AttributeError, TypeError)):
        encoding.bytes_to_int(value)


def test_int_conversion_round_trip():
    values = [0, 1, 2, 255, 256, 65535, 2**32, 2**63, 2**64 - 1]
    for value in values:
        assert encoding.bytes_to_int(encoding.int_to_bytes(value)) == value


def test_int_conversion_round_trip_with_leading_zero_bytes():
    for value in [1, 255, 256, 65535, 2**32 - 1]:
        encoded = encoding.int_to_bytes(value)
        assert encoding.bytes_to_int(encoded) == value
