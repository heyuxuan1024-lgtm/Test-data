
import pytest
import base58


def test_module_constants():
    assert base58.__version__ == "2.1.1"
    assert base58.BITCOIN_ALPHABET == b"123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    assert base58.RIPPLE_ALPHABET == b"rpshnaf39wBUDNEGHJKLM4PQRST7VWXYZ2bcdeCg65jkm8oFqi1tuvAxyz"
    assert base58.XRP_ALPHABET == base58.RIPPLE_ALPHABET
    assert base58.alphabet == base58.BITCOIN_ALPHABET


@pytest.mark.parametrize(
    "value, expected",
    [
        ("hello", b"hello"),
        ("", b""),
        ("123", b"123"),
        (b"hello", b"hello"),
        (b"", b""),
        (b"\x00\xff", b"\x00\xff"),
    ],
)
def test_scrub_input(value, expected):
    assert base58.scrub_input(value) == expected


def test_scrub_input_non_ascii_string():
    with pytest.raises(UnicodeEncodeError):
        base58.scrub_input("你好")


@pytest.mark.parametrize(
    "value, expected",
    [
        (0, b"1"),
        (1, b"2"),
        (57, b"z"),
        (58, b"21"),
        (59, b"22"),
        (12345, b"4ER"),
        (256, b"5Q"),
        (0, b""),
    ],
)
def test_b58encode_int(value, expected):
    if value == 0 and expected == b"":
        assert base58.b58encode_int(value, default_one=False) == expected
    else:
        assert base58.b58encode_int(value) == expected


@pytest.mark.parametrize("value", [0, 1, 57, 58, 12345, 2**256])
def test_b58encode_int_round_trip(value):
    encoded = base58.b58encode_int(value)
    assert base58.b58decode_int(encoded) == value


def test_b58encode_int_custom_alphabet():
    custom = b"abc"
    assert base58.b58encode_int(0, alphabet=custom) == b"a"
    assert base58.b58encode_int(1, alphabet=custom) == b"b"
    assert base58.b58encode_int(2, alphabet=custom) == b"c"
    assert base58.b58encode_int(3, alphabet=custom) == b"ba"
    assert base58.b58encode_int(0, default_one=False, alphabet=custom) == b""


def test_b58encode_int_negative_integer():
    assert base58.b58encode_int(-1) == b""
    assert base58.b58encode_int(-100) == b""


@pytest.mark.parametrize(
    "value, expected",
    [
        (b"", b""),
        (b"\x00", b"1"),
        (b"\x00\x00", b"11"),
        (b"\x01", b"2"),
        (b"\x01\x02", b"5T"),
        (b"hello", b"Cn8eVZg"),
        ("hello", b"Cn8eVZg"),
        (b"\x00hello", b"1Cn8eVZg"),
        (b"\x00\x00hello", b"11Cn8eVZg"),
    ],
)
def test_b58encode(value, expected):
    assert base58.b58encode(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        b"",
        b"\x00",
        b"\x00\x00",
        b"\x01",
        b"\x01\x02",
        b"hello",
        b"\x00hello",
        bytes(range(256)),
    ],
)
def test_b58encode_decode_round_trip(value):
    assert base58.b58decode(base58.b58encode(value)) == value


def test_b58encode_custom_alphabet():
    custom = b"abc"
    assert base58.b58encode(b"\x01", alphabet=custom) == b"b"
    assert base58.b58encode(b"\x02", alphabet=custom) == b"c"
    assert base58.b58encode(b"\x03", alphabet=custom) == b"ba"
    assert base58.b58decode(base58.b58encode(b"\x01\x02", alphabet=custom), alphabet=custom) == b"\x01\x02"


def test_b58encode_leading_zero_bytes():
    assert base58.b58encode(b"\x00\x00\x01") == b"112"
    assert base58.b58encode(b"\x00\x00\x00") == b"111"
    assert base58.b58decode(b"112") == b"\x00\x00\x01"
    assert base58.b58decode(b"111") == b"\x00\x00\x00"


@pytest.mark.parametrize(
    "value, expected",
    [
        (b"", 0),
        (b"1", 0),
        (b"2", 1),
        (b"z", 57),
        (b"21", 58),
        (b"22", 59),
        (b"4ER", 12345),
        ("4ER", 12345),
        (b"2 ", 1),
        (b"2\n", 1),
        (b"2\t", 1),
    ],
)
def test_b58decode_int(value, expected):
    assert base58.b58decode_int(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        b"",
        b"1",
        b"2",
        b"z",
        b"21",
        b"4ER",
        b"123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz",
        b"2" * 100,
    ],
)
def test_b58decode_int_round_trip(value):
    assert base58.b58encode_int(base58.b58decode_int(value)) == value.lstrip(b"1") or (
        value.startswith(b"1") and base58.b58decode_int(value) == 0
    )


@pytest.mark.parametrize(
    "value",
    [
        b"0",
        b"O",
        b"I",
        b"l",
        b"!",
        b"@",
        b"\xff",
    ],
)
def test_b58decode_int_invalid_character(value):
    with pytest.raises(ValueError, match="Invalid character"):
        base58.b58decode_int(value)


def test_b58decode_int_invalid_character_message():
    with pytest.raises(ValueError, match=r"Invalid character '0'"):
        base58.b58decode_int(b"0")


def test_b58decode_int_custom_alphabet():
    custom = b"abc"
    assert base58.b58decode_int(b"a", alphabet=custom) == 0
    assert base58.b58decode_int(b"b", alphabet=custom) == 1
    assert base58.b58decode_int(b"c", alphabet=custom) == 2
    assert base58.b58decode_int(b"ba", alphabet=custom) == 3


def test_b58decode_int_alphabet_with_space():
    custom = b"ab "
    assert base58.b58decode_int(b"a ", alphabet=custom) == 2
    with pytest.raises(ValueError):
        base58.b58decode_int(b"a ", alphabet=b"abc")


@pytest.mark.parametrize(
    "value, expected",
    [
        (b"", b""),
        (b"1", b"\x00"),
        (b"11", b"\x00\x00"),
        (b"2", b"\x01"),
        (b"5T", b"\x01\x02"),
        (b"Cn8eVZg", b"hello"),
        ("Cn8eVZg", b"hello"),
        (b"1Cn8eVZg", b"\x00hello"),
        (b"11Cn8eVZg", b"\x00\x00hello"),
        (b"2 ", b"\x01"),
    ],
)
def test_b58decode(value, expected):
    assert base58.b58decode(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        b"0",
        b"O",
        b"I",
        b"l",
        b"!",
        b"invalid",
        b"\xff",
    ],
)
def test_b58decode_invalid_character(value):
    with pytest.raises(ValueError):
        base58.b58decode(value)


def test_b58decode_autofix_compatible_alphabet():
    assert base58.b58decode_int(b"0", autofix=True) == 0
    assert base58.b58decode_int(b"O", autofix=True) == 0
    assert base58.b58decode_int(b"I", autofix=True) == 0
    assert base58.b58decode_int(b"l", autofix=True) == 0


def test_b58decode_autofix_disabled():
    for value in (b"0", b"O", b"I", b"l"):
        with pytest.raises(ValueError):
            base58.b58decode_int(value, autofix=False)


def test_b58decode_autofix_custom_alphabet():
    custom = b"0abc"
    assert base58.b58decode_int(b"O", alphabet=custom, autofix=True) == 0


def test_b58decode_autofix_mapping_cache():
    first = base58._get_base58_decode_map(base58.BITCOIN_ALPHABET, True)
    second = base58._get_base58_decode_map(base58.BITCOIN_ALPHABET, True)
    assert first is second
    assert base58._get_base58_decode_map.cache_info().hits >= 1


def test_b58decode_custom_alphabet():
    custom = b"abc"
    assert base58.b58decode(b"b", alphabet=custom) == b"\x01"
    assert base58.b58decode(b"c", alphabet=custom) == b"\x02"
    assert base58.b58decode(b"ba", alphabet=custom) == b"\x03"


def test_b58decode_empty_and_all_leading_alphabet_characters():
    assert base58.b58decode(b"") == b""
    assert base58.b58decode(b"111") == b"\x00\x00\x00"


def test_b58decode_whitespace_stripping():
    assert base58.b58decode(b"2 \n\t") == b"\x01"
    assert base58.b58decode_int(b"2 \n\t") == 1


def test_b58decode_non_ascii_string():
    with pytest.raises(UnicodeEncodeError):
        base58.b58decode("é")


def test_b58decode_int_non_ascii_string():
    with pytest.raises(UnicodeEncodeError):
        base58.b58decode_int("é")


def test_b58encode_non_ascii_string():
    with pytest.raises(UnicodeEncodeError):
        base58.b58encode("é")


def test_b58encode_check_known_vector():
    assert base58.b58encode_check(b"hello") == b"2L5B5yqsVG8Vt"


def test_b58encode_check_string_input():
    assert base58.b58encode_check("hello") == base58.b58encode_check(b"hello")


@pytest.mark.parametrize(
    "value",
    [
        b"",
        b"hello",
        b"\x00",
        b"\x00\x00hello",
        bytes(range(256)),
    ],
)
def test_b58encode_check_decode_round_trip(value):
    encoded = base58.b58encode_check(value)
    assert base58.b58decode_check(encoded) == value


def test_b58encode_check_custom_alphabet():
    custom = base58.RIPPLE_ALPHABET
    encoded = base58.b58encode_check(b"hello", alphabet=custom)
    assert base58.b58decode_check(encoded, alphabet=custom) == b"hello"


def test_b58decode_check_invalid_checksum():
    encoded = bytearray(base58.b58encode_check(b"hello"))
    encoded[-1] = ord("1") if encoded[-1] != ord("1") else ord("2")
    with pytest.raises(ValueError, match="Invalid checksum"):
        base58.b58decode_check(bytes(encoded))


def test_b58decode_check_too_short():
    with pytest.raises(ValueError, match="Invalid checksum"):
        base58.b58decode_check(base58.b58encode(b"abc"))


def test_b58decode_check_invalid_base58():
    with pytest.raises(ValueError, match="Invalid character"):
        base58.b58decode_check(b"0")


def test_b58decode_check_autofix():
    encoded = base58.b58encode_check(b"hello")
    altered = encoded.replace(b"1", b"l")
    assert base58.b58decode_check(altered, autofix=True) == b"hello"


@pytest.mark.parametrize(
    "alphabet",
    [
        b"",
        b"a",
        b"abc",
        b"0123456789",
        base58.RIPPLE_ALPHABET,
        base58.BITCOIN_ALPHABET,
    ],
)
def test_custom_alphabet_integer_round_trip(alphabet):
    for value in (0, 1, 2, 10, 58, 1234, 2**128):
        encoded = base58.b58encode_int(value, alphabet=alphabet)
        if alphabet:
            decoded = base58.b58decode_int(encoded, alphabet=alphabet)
            assert decoded == value


def test_decode_map_autofix_groups_with_multiple_pivots():
    custom = b"0OIl1abc"
    mapping = base58._get_base58_decode_map(custom, True)
    assert mapping[ord("0")] == 0
    assert mapping[ord("O")] == 1
    assert mapping[ord("I")] == 2
    assert mapping[ord("l")] == 2
    assert mapping[ord("1")] == 2


def test_decode_map_autofix_group_without_pivot():
    custom = b"abc"
    mapping = base58._get_base58_decode_map(custom, True)
    assert ord("0") not in mapping
    assert ord("O") not in mapping
    assert ord("I") not in mapping
    assert ord("l") not in mapping
    assert ord("1") not in mapping


def test_b58encode_int_large_number():
    value = 2**4096
    encoded = base58.b58encode_int(value)
    assert base58.b58decode_int(encoded) == value


def test_b58decode_int_large_number():
    value = 2**4096
    encoded = base58.b58encode_int(value)
    assert base58.b58decode_int(encoded) == value


def test_b58encode_empty_custom_alphabet():
    assert base58.b58encode_int(0, alphabet=b"") == b""
    assert base58.b58encode_int(10, alphabet=b"") == b""


def test_b58decode_empty_custom_alphabet():
    assert base58.b58decode_int(b"") == 0
    with pytest.raises(ZeroDivisionError):
        base58.b58decode_int(b"1", alphabet=b"")


def test_b58encode_check_preserves_leading_zeroes():
    value = b"\x00\x00\x01"
    assert base58.b58decode_check(base58.b58encode_check(value)) == value


def test_b58decode_check_custom_alphabet_invalid_checksum():
    encoded = base58.b58encode_check(b"hello", alphabet=base58.RIPPLE_ALPHABET)
    with pytest.raises(ValueError, match="Invalid checksum"):
        base58.b58decode_check(encoded, alphabet=base58.BITCOIN_ALPHABET)
