import pytest
from humanize.filesize import naturalsize

def test_naturalsize_bytes():
    assert naturalsize(0) == "0 Bytes"
    assert naturalsize(1) == "1 Byte"
    assert naturalsize(-1) == "-1 Byte"
    assert naturalsize(500) == "500 Bytes"
    assert naturalsize(-500) == "-500 Bytes"

def test_naturalsize_decimal():
    assert naturalsize(1000) == "1.0 kB"
    assert naturalsize(3000000) == "3.0 MB"
    assert naturalsize(10**28) == "10.0 RB"

def test_naturalsize_binary():
    assert naturalsize(1024, binary=True) == "1.0 KiB"
    assert naturalsize(3000, binary=True) == "2.9 KiB"
    assert naturalsize(-4096, binary=True) == "-4.0 KiB"

def test_naturalsize_gnu():
    assert naturalsize(300, gnu=True) == "300B"
    assert naturalsize(3000, gnu=True) == "2.9K"
    assert naturalsize(3000, gnu=True, format="%.3f") == "2.930K"

def test_naturalsize_string_input():
    assert naturalsize("500") == "500 Bytes"
    assert naturalsize("1000") == "1.0 kB"

def test_naturalsize_rounding_edge_case():
    assert naturalsize(999999, format="%.1f") == "1.0 MB"

def test_naturalsize_extremely_large():
    assert naturalsize(10**34 * 3) == "30000.0 QB"

def test_naturalsize_invalid_value():
    with pytest.raises(ValueError):
        naturalsize("not-a-number")