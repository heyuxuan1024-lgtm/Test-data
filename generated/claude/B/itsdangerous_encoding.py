import base64
import struct

import pytest

from itsdangerous import encoding


def test_want_bytes_str_default_encoding():
    assert encoding.want_bytes("abc") == b"abc"


def test_want_bytes_bytes_passthrough():
    data = b"abc"
    assert encoding.want_bytes(data) is data


def test_want_bytes_empty():
    assert encoding.want_bytes("") == b""
    assert encoding.want_bytes(b"") == b""


def test_want_bytes_utf8_non_ascii():
    assert encoding.want_bytes("caf\u00e9") == "caf\u00e9".encode("utf-8")


def test_want_bytes_custom_encoding():
    assert encoding.want_bytes("caf\u00e9", encoding="latin-1") == b"caf\xe9"
    assert encoding.want_bytes("hi", encoding="utf-16") == "hi".encode("utf-16")


def test_want_bytes_errors_strict_raises():
    with pytest.raises(UnicodeEncodeError):
        encoding.want_bytes("caf\u00e9", encoding="ascii")


def test_want_bytes_errors_ignore():
    assert encoding.want_bytes("caf\u00e9", encoding="ascii", errors="ignore") == b"caf"


def test_want_bytes_errors_replace():
    assert encoding.want_bytes("caf\u00e9", encoding="ascii", errors="replace") == b"caf?"


def test_want_bytes_unknown_encoding_raises():
    with pytest.raises(LookupError):
        encoding.want_bytes("abc", encoding="not-a-real-codec")


def test_want_bytes_bytes_ignores_encoding_args():
    assert encoding.want_bytes(b"\xff", encoding="not-a-real-codec") == b"\xff"


@pytest.mark.parametrize("data", [None, 123, 1.5, [1, 2], bytearray(b"abc")])
def test_want_bytes_non_str_non_bytes_passthrough(data):
    assert encoding.want_bytes(data) is data


@pytest.mark.parametrize(
    "data, expected",
    [
        (b"", b""),
        (b"f", b"Zg"),
        (b"fo", b"Zm8"),
        (b"foo", b"Zm9v"),
        (b"foob", b"Zm9vYg"),
        (b"fooba", b"Zm9vYmE"),
        (b"foobar", b"Zm9vYmFy"),
        (b"\xfb\xff", b"-_8"),
        (b"\xff\xff\xff", b"____"),
    ],
)
def test_base64_encode_known_vectors(data, expected):
    assert encoding.base64_encode(data) == expected


def test_base64_encode_str_input():
    assert encoding.base64_encode("foobar") == b"Zm9vYmFy"
    assert encoding.base64_encode("") == b""


def test_base64_encode_non_ascii_str_uses_utf8():
    assert encoding.base64_encode("caf\u00e9") == encoding.base64_encode(
        "caf\u00e9".encode("utf-8")
    )


def test_base64_encode_has_no_padding():
    for length in range(0, 12):
        assert b"=" not in encoding.base64_encode(b"x" * length)


def test_base64_encode_is_url_safe():
    encoded = encoding.base64_encode(bytes(range(256)))
    assert b"+" not in encoded
    assert b"/" not in encoded
    assert set(encoded) <= set(encoding._base64_alphabet) - {ord("=")}


def test_base64_encode_invalid_type_raises():
    with pytest.raises(TypeError):
        encoding.base64_encode(None)
    with pytest.raises(TypeError):
        encoding.base64_encode(123)


@pytest.mark.parametrize(
    "encoded, expected",
    [
        (b"", b""),
        (b"Zg", b"f"),
        (b"Zm8", b"fo"),
        (b"Zm9v", b"foo"),
        (b"Zm9vYg", b"foob"),
        (b"Zm9vYmE", b"fooba"),
        (b"Zm9vYmFy", b"foobar"),
        (b"-_8", b"\xfb\xff"),
        (b"____", b"\xff\xff\xff"),
    ],
)
def test_base64_decode_known_vectors(encoded, expected):
    assert encoding.base64_decode(encoded) == expected


def test_base64_decode_str_input():
    assert encoding.base64_decode("Zm9vYmFy") == b"foobar"
    assert encoding.base64_decode("") == b""


def test_base64_decode_accepts_existing_padding():
    assert encoding.base64_decode(b"Zg==") == b"f"
    assert encoding.base64_decode(b"Zm8=") == b"fo"
    assert encoding.base64_decode("Zg==") == b"f"


def test_base64_decode_non_ascii_str_chars_are_ignored():
    assert encoding.base64_decode("Zm9v\u00e9") == b"foo"
    assert encoding.base64_decode("\u00e9Zm9v") == b"foo"


def test_base64_decode_non_alphabet_bytes_are_discarded_by_stdlib():
    assert encoding.base64_decode(b"Zm9v!!!!") == b"foo"
    assert encoding.base64_decode(b"Zm 9v") == b"foo"
    assert encoding.base64_decode(b"Zm\n9v") == b"foo"


def test_base64_decode_standard_alphabet_chars_not_translated():
    assert encoding.base64_decode(b"+/") != encoding.base64_decode(b"-_")


def test_base64_decode_invalid_padding_raises_bad_data():
    with pytest.raises(encoding.BadData, match="Invalid base64-encoded data"):
        encoding.base64_decode(b"Z")


def test_base64_decode_invalid_length_raises_bad_data():
    with pytest.raises(encoding.BadData):
        encoding.base64_decode(b"Zm9vY")


def test_base64_decode_excess_padding_raises_bad_data():
    with pytest.raises(encoding.BadData):
        encoding.base64_decode(b"Zg=====")


def test_base64_decode_wraps_original_exception():
    with pytest.raises(encoding.BadData) as info:
        encoding.base64_decode(b"Z")
    assert isinstance(info.value.__cause__, (TypeError, ValueError))
    assert info.value.message == "Invalid base64-encoded data"


def test_base64_decode_wraps_type_error(monkeypatch):
    def boom(_):
        raise TypeError("boom")

    monkeypatch.setattr(encoding.base64, "urlsafe_b64decode", boom)
    with pytest.raises(encoding.BadData) as info:
        encoding.base64_decode(b"Zm9v")
    assert isinstance(info.value.__cause__, TypeError)


def test_base64_decode_wraps_value_error(monkeypatch):
    def boom(_):
        raise ValueError("boom")

    monkeypatch.setattr(encoding.base64, "urlsafe_b64decode", boom)
    with pytest.raises(encoding.BadData) as info:
        encoding.base64_decode(b"Zm9v")
    assert isinstance(info.value.__cause__, ValueError)


def test_base64_decode_invalid_type_raises_type_error():
    with pytest.raises(TypeError):
        encoding.base64_decode(None)
    with pytest.raises(TypeError):
        encoding.base64_decode(123)


@pytest.mark.parametrize(
    "data",
    [
        b"",
        b"\x00",
        b"\x00\x00\x00",
        b"\xff",
        b"hello world",
        bytes(range(256)),
        b"\xfb\xff\xfe" * 7,
    ],
)
def test_base64_roundtrip(data):
    assert encoding.base64_decode(encoding.base64_encode(data)) == data


def test_base64_encode_matches_stdlib():
    data = bytes(range(256))
    assert encoding.base64_encode(data) == base64.urlsafe_b64encode(data).rstrip(b"=")


def test_base64_alphabet_constant():
    alphabet = encoding._base64_alphabet
    assert isinstance(alphabet, bytes)
    assert len(alphabet) == 65
    assert alphabet.endswith(b"-_=")
    assert b"+" not in alphabet
    assert b"/" not in alphabet
    assert alphabet.startswith(
        b"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    )


def test_int_struct_constants():
    assert encoding._int64_struct.format == ">Q"
    assert encoding._int64_struct.size == 8
    assert encoding._int_to_bytes == encoding._int64_struct.pack
    assert encoding._bytes_to_int == encoding._int64_struct.unpack


@pytest.mark.parametrize(
    "num, expected",
    [
        (0, b""),
        (1, b"\x01"),
        (255, b"\xff"),
        (256, b"\x01\x00"),
        (65535, b"\xff\xff"),
        (65536, b"\x01\x00\x00"),
        (2**32, b"\x01\x00\x00\x00\x00"),
        (2**56, b"\x01" + b"\x00" * 7),
        (2**64 - 1, b"\xff" * 8),
    ],
)
def test_int_to_bytes(num, expected):
    assert encoding.int_to_bytes(num) == expected


def test_int_to_bytes_negative_raises():
    with pytest.raises(struct.error):
        encoding.int_to_bytes(-1)


def test_int_to_bytes_overflow_raises():
    with pytest.raises(struct.error):
        encoding.int_to_bytes(2**64)


@pytest.mark.parametrize("bad", [None, "1", 1.5, b"\x01"])
def test_int_to_bytes_invalid_type_raises(bad):
    with pytest.raises(struct.error):
        encoding.int_to_bytes(bad)


@pytest.mark.parametrize(
    "data, expected",
    [
        (b"", 0),
        (b"\x00", 0),
        (b"\x01", 1),
        (b"\xff", 255),
        (b"\x01\x00", 256),
        (b"\x00\x01", 1),
        (b"\x00\x00\x00\x01", 1),
        (b"\x01\x00\x00\x00\x00", 2**32),
        (b"\x01" + b"\x00" * 7, 2**56),
        (b"\xff" * 8, 2**64 - 1),
        (b"\x00" * 8, 0),
    ],
)
def test_bytes_to_int(data, expected):
    assert encoding.bytes_to_int(data) == expected


def test_bytes_to_int_too_long_raises():
    with pytest.raises(struct.error):
        encoding.bytes_to_int(b"\x01" * 9)


def test_bytes_to_int_invalid_type_raises():
    with pytest.raises(AttributeError):
        encoding.bytes_to_int(None)
    with pytest.raises(AttributeError):
        encoding.bytes_to_int(5)


@pytest.mark.parametrize(
    "num",
    [0, 1, 127, 128, 255, 256, 12345, 2**31, 2**32 - 1, 2**48, 2**63, 2**64 - 1],
)
def test_int_roundtrip(num):
    assert encoding.bytes_to_int(encoding.int_to_bytes(num)) == num


def test_int_to_bytes_strips_leading_zeros_only():
    assert encoding.int_to_bytes(0x0100) == b"\x01\x00"
    assert encoding.int_to_bytes(0x00FF) == b"\xff"
    assert not encoding.int_to_bytes(12345).startswith(b"\x00")


def test_bytes_to_int_pads_short_input_with_leading_zeros():
    assert encoding.bytes_to_int(b"\x05") == encoding.bytes_to_int(
        b"\x00\x00\x00\x00\x00\x00\x00\x05"
    )