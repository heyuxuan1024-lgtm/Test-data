
import base64
import pytest

from your_module import (
    BadData,
    want_bytes,
    base64_encode,
    base64_decode,
    int_to_bytes,
    bytes_to_int,
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("hello", b"hello"),
        ("", b""),
        ("你好", "你好".encode("utf-8")),
        (b"hello", b"hello"),
        (b"", b""),
        (b"\x00\xff", b"\x00\xff"),
    ],
)
def test_want_bytes(value, expected):
    assert want_bytes(value) == expected


def test_want_bytes_custom_encoding():
    assert want_bytes("café", encoding="latin-1") == b"caf\xe9"


def test_want_bytes_custom_error_handling():
    assert want_bytes("你好", encoding="ascii", errors="ignore") == b""


def test_want_bytes_replace_errors():
    assert want_bytes("你好", encoding="ascii", errors="replace") == b"??"


def test_want_bytes_strict_encoding_error():
    with pytest.raises(UnicodeEncodeError):
        want_bytes("你好", encoding="ascii")


def test_want_bytes_invalid_encoding():
    with pytest.raises(LookupError):
        want_bytes("hello", encoding="invalid-encoding")


def test_want_bytes_non_string_passthrough():
    value = bytearray(b"hello")
    assert want_bytes(value) is value


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("", b""),
        ("hello", b"aGVsbG8"),
        ("f", b"Zg"),
        ("fo", b"Zm8"),
        ("foo", b"Zm9v"),
        ("foobar", b"Zm9vYmFy"),
        (b"hello", b"aGVsbG8"),
        (b"\x00\xff", b"AP8"),
        ("你好", "你好".encode("utf-8") and base64.urlsafe_b64encode("你好".encode()).rstrip(b"=")),
    ],
)
def test_base64_encode(value, expected):
    assert base64_encode(value) == expected


def test_base64_encode_url_safe_characters():
    encoded = base64_encode(b"\xfb\xff")
    assert encoded == b"-_8"
    assert b"+" not in encoded
    assert b"/" not in encoded
    assert b"=" not in encoded


def test_base64_encode_returns_bytes():
    assert isinstance(base64_encode("hello"), bytes)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("", b""),
        (b"", b""),
        ("aGVsbG8", b"hello"),
        (b"aGVsbG8", b"hello"),
        ("Zg", b"f"),
        ("Zm8", b"fo"),
        ("Zm9v", b"foo"),
        ("Zm9vYmFy", b"foobar"),
        ("-_8", b"\xfb\xff"),
        ("AP8", b"\x00\xff"),
        ("aGVsbG8=", b"hello"),
        ("aGVsbG8==", b"hello"),
    ],
)
def test_base64_decode(value, expected):
    assert base64_decode(value) == expected


def test_base64_decode_adds_padding_for_remainder_one():
    assert base64_decode("YQ") == b"a"


def test_base64_decode_adds_padding_for_remainder_two():
    assert base64_decode("YWI") == b"ab"


def test_base64_decode_adds_padding_for_remainder_three():
    assert base64_decode("YWJj") == b"abc"


def test_base64_decode_ignores_non_ascii_characters():
    assert base64_decode("aGVs你好bG8") == b"hello"


def test_base64_decode_ascii_bytes():
    assert base64_decode(b"aGVsbG8") == b"hello"


def test_base64_decode_returns_bytes():
    assert isinstance(base64_decode("aGVsbG8"), bytes)


def test_base64_decode_invalid_input_type():
    with pytest.raises(TypeError):
        base64_decode(123)


def test_base64_decode_invalid_base64_data():
    with pytest.raises(BadData) as exc_info:
        base64_decode("!!!!")
    assert str(exc_info.value) == "Invalid base64-encoded data"


def test_base64_decode_invalid_padding():
    with pytest.raises(BadData):
        base64_decode("a===")


def test_base64_decode_empty_string():
    assert base64_decode("") == b""


@pytest.mark.parametrize(
    ("number", "expected"),
    [
        (0, b""),
        (1, b"\x01"),
        (2, b"\x02"),
        (255, b"\xff"),
        (256, b"\x01\x00"),
        (65535, b"\xff\xff"),
        (65536, b"\x01\x00\x00"),
        (2**32 - 1, b"\xff\xff\xff\xff"),
        (2**32, b"\x01\x00\x00\x00\x00"),
        (2**64 - 1, b"\xff" * 8),
    ],
)
def test_int_to_bytes(number, expected):
    assert int_to_bytes(number) == expected


def test_int_to_bytes_zero():
    assert int_to_bytes(0) == b""


def test_int_to_bytes_leading_zero_bytes_are_removed():
    assert int_to_bytes(0x00000102) == b"\x01\x02"


@pytest.mark.parametrize(
    "number",
    [
        -1,
        -100,
        2**64,
        2**100,
    ],
)
def test_int_to_bytes_out_of_range(number):
    with pytest.raises(struct.error):
        int_to_bytes(number)


def test_int_to_bytes_non_integer():
    with pytest.raises(struct.error):
        int_to_bytes(1.5)


def test_int_to_bytes_none():
    with pytest.raises(struct.error):
        int_to_bytes(None)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (b"", 0),
        (b"\x00", 0),
        (b"\x01", 1),
        (b"\x02", 2),
        (b"\xff", 255),
        (b"\x01\x00", 256),
        (b"\xff\xff", 65535),
        (b"\x01\x00\x00", 65536),
        (b"\xff" * 4, 2**32 - 1),
        (b"\x01\x00\x00\x00\x00", 2**32),
        (b"\xff" * 8, 2**64 - 1),
        (b"\x00\x00\x00\x00\x00\x00\x00\x01", 1),
    ],
)
def test_bytes_to_int(value, expected):
    assert bytes_to_int(value) == expected


def test_bytes_to_int_longer_than_eight_bytes():
    assert bytes_to_int(b"\x01" + b"\x00" * 8) == 2**56


def test_bytes_to_int_right_pads_short_input_with_zeroes():
    assert bytes_to_int(b"\x01") == 1


def test_bytes_to_int_non_bytes_input():
    with pytest.raises(TypeError):
        bytes_to_int("123")


def test_bytes_to_int_bytearray_input():
    assert bytes_to_int(bytearray(b"\x01")) == 1


def test_bytes_to_int_none():
    with pytest.raises(AttributeError):
        bytes_to_int(None)


def test_integer_conversion_round_trip():
    values = [
        0,
        1,
        255,
        256,
        65535,
        65536,
        2**32,
        2**63,
        2**64 - 1,
    ]

    for value in values:
        assert bytes_to_int(int_to_bytes(value)) == value


def test_base64_round_trip():
    values = [
        "",
        "hello",
        "你好",
        "café",
        b"\x00\x01\x02",
        b"\xfb\xff\x00\x80",
        bytes(range(256)),
    ]

    for value in values:
        assert base64_decode(base64_encode(value)) == (
            value.encode("utf-8") if isinstance(value, str) else value
        )
