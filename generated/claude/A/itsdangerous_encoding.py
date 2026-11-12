import base64
import struct

import pytest

from itsdangerous import encoding
from itsdangerous.encoding import (
    base64_decode,
    base64_encode,
    bytes_to_int,
    int_to_bytes,
    want_bytes,
)
from itsdangerous.exc import BadData


def test_want_bytes_str_default_encoding():
    assert want_bytes("abc") == b"abc"


def test_want_bytes_bytes_passthrough():
    data = b"abc"
    assert want_bytes(data) is data


def test_want_bytes_empty():
    assert want_bytes("") == b""
    assert want_bytes(b"") == b""


def test_want_bytes_utf8_non_ascii():
    assert want_bytes("caf\u00e9") == "caf\u00e9".encode("utf-8")


def test_want_bytes_custom_encoding():
    assert want_bytes("caf\u00e9", encoding="latin-1") == b"caf\xe9"
    assert want_bytes("hi", encoding="utf-16") == "hi".encode("utf-16")


def test_want_bytes_errors_strict_raises():
    with pytest.raises(UnicodeEncodeError):
        want_bytes("caf\u00e9", encoding="ascii")


def test_want_bytes_errors_ignore():
    assert want_bytes("caf\u00e9", encoding="ascii", errors="ignore") == b"caf"


def test_want_bytes_errors_replace():
    assert want_bytes("caf\u00e9", encoding="ascii", errors="replace") == b"caf?"


def test_want_bytes_unknown_encoding_raises():
    with pytest.raises(LookupError):
        want_bytes("abc", encoding="not-a-real-codec")


def test_want_bytes_bytes_ignores_encoding_args():
    assert want_bytes(b"\xff", encoding="not-a-real-codec") == b"\xff"


@pytest.mark.parametrize("data", [None, 123, 1.5, [1, 2], bytearray(b"abc")])
def test_want_bytes_non_str_non_bytes_passthrough(data):
    assert want_bytes(data) is data


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
    assert base64_encode(data) == expected


def test_base64_encode_str_input():
    assert base64_encode("foobar") == b"Zm9vYmFy"