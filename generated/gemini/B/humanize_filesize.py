import pytest
from humanize import filesize

def test_naturalsize_bytes():
    assert filesize.naturalsize(0) == "0 Bytes"
    assert filesize.naturalsize(1) == "1 Byte"
    assert filesize.naturalsize(-1) == "-1 Byte"
    assert filesize.naturalsize(500) == "500 Bytes"
    assert filesize.naturalsize(-500) == "-500 Bytes"

def test_naturalsize_decimal():
    assert filesize.naturalsize(1000) == "1.0 kB"
    assert filesize.naturalsize(3000000) == "3.0 MB"
    assert filesize.naturalsize(10**28) == "10.0 RB"

def test_naturalsize_binary():
    assert filesize.naturalsize(1024, binary=True) == "1.0 KiB"
    assert filesize.naturalsize(3000, binary=True) == "2.9 KiB"
    assert filesize.naturalsize(-4096, binary=True) == "-4.0 KiB"

def test_naturalsize_gnu():
    assert filesize.naturalsize(300, gnu=True) == "300B"
    assert filesize.naturalsize(3000, gnu=True) == "2.9K"
    assert filesize.naturalsize(3000, gnu=True, format="%.3f") == "2.930K"

def test_naturalsize_string_input():
    assert filesize.naturalsize("500") == "500 Bytes"
    assert filesize.naturalsize("1000") == "1.0 kB"

def test_naturalsize_rounding_edge_case():
    assert filesize.naturalsize(999999, format="%.1f") == "1.0 MB"

def test_naturalsize_extremely_large():
    assert filesize.naturalsize(10**34 * 3) == "30000.0 QB"

def test_naturalsize_invalid_value():
    with pytest.raises(ValueError):
        filesize.naturalsize("not-a-number")