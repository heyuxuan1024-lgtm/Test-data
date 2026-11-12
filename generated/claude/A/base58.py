import hashlib

import pytest

import base58
from base58 import (
    BITCOIN_ALPHABET,
    RIPPLE_ALPHABET,
    XRP_ALPHABET,
    _get_base58_decode_map,
    b58decode,
    b58decode_check,
    b58decode_int,
    b58encode,
    b58encode_check,
    b58encode_int,
    scrub_input,
)

SPACE_ALPHABET = BITCOIN_ALPHABET[:-1] + b' '
NO_FIX_ALPHABET = b'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUV'
NO_ZERO_GROUP_ALPHABET = b'abcdefghijklmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ123456789'


def test_module_constants():
    assert base58.__version__ == '2.1.1'
    assert len(BITCOIN_ALPHABET) == 58
    assert len(RIPPLE_ALPHABET) == 58
    assert len(set(BITCOIN_ALPHABET)) == 58
    assert len(set(RIPPLE_ALPHABET)) == 58
    assert XRP_ALPHABET is RIPPLE_ALPHABET
    assert base58.alphabet is BITCOIN_ALPHABET
    assert len(SPACE_ALPHABET) == 58
    assert len(NO_FIX_ALPHABET) == 58
    assert len(NO_ZERO_GROUP_ALPHABET) == 58


def test_scrub_input_str_is_encoded():
    assert scrub_input('abc') == b'abc'


def test_scrub_input_bytes_passthrough():
    data = b'abc'
    assert scrub_input(data) is data


def test_scrub_input_empty_str():
    assert scrub_input('') == b''


def test_scrub_input_non_ascii_raises():
    with pytest.raises(UnicodeEncodeError):
        scrub_input('caf\u00e9')


def test_b58encode_int_zero_default_one():
    assert b58encode_int(0) == b'1'


def test_b58encode_int_zero_without_default_one():
    assert b58encode_int(0, default_one=False) == b''


def test_b58encode_int_zero_custom_alphabet():
    assert b58encode_int(0, alphabet=RIPPLE_ALPHABET) == b'r'


@pytest.mark.parametrize(
    'value, expected',
    [
        (1, b'2'),
        (57, b'z'),
        (58, b'21'),
        (59, b'22'),
        (58 * 58, b'211'),
    ],
)
def test_b58encode_int_values(value, expected):
    assert b58encode_int(value) == expected


def test_b58encode_int_custom_alphabet():
    assert b58encode_int(1, alphabet=RIPPLE_ALPHABET) == RIPPLE_ALPHABET[1:2]
    assert b58encode_int(58, alphabet=RIPPLE_ALPHABET) == RIPPLE_ALPHABET[1:2] + RIPPLE_ALPHABET[0:1]


def test_b58encode_int_small_alphabet():
    assert b58encode_int(5, alphabet=b'01') == b'101'


def test_b58encode_int_negative_returns_non_terminating_guard():
    assert b58encode_int(-0) == b'1'


def test_b58encode_empty():
    assert b58encode(b'') == b''
    assert b58encode('') == b''


def test_b58encode_single_zero_byte():
    assert b58encode(b'\x00') == b'1'


def test_b58encode_multiple_zero_bytes():
    assert b58encode(b'\x00\x00\x00') == b'111'


def test_b58encode_known_vectors():
    assert b58encode(b'hello world') == b'StV1DL6CwTryKyV'
    assert b58encode(b'Hello World!') == b'2NEpo7TZRRrLZSi2U'


def test_b58encode_str_input():
    assert b58encode('hello world') == b'StV1DL6CwTryKyV'


def test_b58encode_leading_zeros_preserved():
    assert b58encode(b'\x00\x00hello world') == b'11StV1DL6CwTryKyV'


def test_b58encode_ripple_alphabet():
    assert b58encode(b'\x00', alphabet=RIPPLE_ALPHABET) == b'r'
    assert b58encode(b'\x00\x00', alphabet=RIPPLE_ALPHABET) == b'rr'
    assert b58encode(b'\x01', alphabet=RIPPLE_ALPHABET) == RIPPLE_ALPHABET[1:2]


def test_b58encode_non_ascii_str_raises():
    with pytest.raises(UnicodeEncodeError):
        b58encode('caf\u00e9')


@pytest.mark.parametrize('bad', [None, 123, 1.5, [1, 2, 3]])
def test_b58encode_invalid_type_raises(bad):
    with pytest.raises(TypeError):
        b58encode(bad)


def test_b58decode_int_basic():
    assert b58decode_int(b'1') == 0
    assert b58decode_int('2') == 1
    assert b58decode_int(b'z') == 57
    assert b58decode_int('21') == 58


def test_b58decode_int_empty():
    assert b58decode_int(b'') == 0
    assert b58decode_int('') == 0


def test_b58decode_int_strips_trailing_whitespace():
    assert b58decode_int('21 ') == 58
    assert b58decode_int(b'21\n') == 58
    assert b58decode_int('21 \t\n') == 58


def test_b58decode_int_space_in_alphabet_not_stripped():
    assert b58decode_int('1 ', alphabet=SPACE_ALPHABET) == 57
    assert b58decode_int(b'1 ', alphabet=SPACE_ALPHABET) == 57


def test_b58decode_int_space_not_in_alphabet_is_stripped():
    assert b58decode_int('1 ') == 0


def test_b58decode_int_invalid_character_message():
    with pytest.raises(ValueError, match="Invalid character '0'"):
        b58decode_int('0')


@pytest.mark.parametrize('bad', ['0', 'O', 'I', 'l', '!', 'a-b', '\x7f'])
def test_b58decode_int_invalid_characters(bad):
    with pytest.raises(ValueError, match='Invalid character'):
        b58decode_int(bad)


def test_b58decode_int_invalid_character_in_middle():
    with pytest.raises(ValueError, match="Invalid character 'l'"):
        b58decode_int(b'abcl')


def test_b58decode_int_invalid_internal_space():
    with pytest.raises(ValueError, match="Invalid character ' '"):
        b58decode_int('2 2')


def test_b58decode_int_no_exception_chaining_context():
    with pytest.raises(ValueError) as info:
        b58decode_int('0')
    assert info.value.__cause__ is None
    assert info.value.__suppress_context__ is True


def test_b58decode_int_non_ascii_raises():
    with pytest.raises(UnicodeEncodeError):
        b58decode_int('caf\u00e9')


def test_b58decode_int_autofix_zero_group():
    expected = b58decode_int('o')
    assert b58decode_int('0', autofix=True) == expected
    assert b58decode_int('O', autofix=True) == expected
    assert b58decode_int('o', autofix=True) == expected


def test_b58decode_int_autofix_one_group():
    assert b58decode_int('I', autofix=True) == 0
    assert b58decode_int('l', autofix=True) == 0
    assert b58decode_int('1', autofix=True) == 0


def test_b58decode_int_autofix_default_is_off():
    with pytest.raises(ValueError):
        b58decode_int('0')
    with pytest.raises(ValueError):
        b58decode_int('I')


def test_b58decode_int_autofix_mixed_string():
    assert b58decode_int('l0', autofix=True) == b58decode_int('1o')


def test_b58decode_int_autofix_other_invalid_still_raises():
    with pytest.raises(ValueError, match="Invalid character '!'"):
        b58decode_int('!', autofix=True)


def test_b58decode_int_custom_alphabet():
    assert b58decode_int('s', alphabet=RIPPLE_ALPHABET) == 2
    assert b58decode_int(b'rp', alphabet=RIPPLE_ALPHABET) == 1


def test_b58decode_int_invalid_type_raises():
    with pytest.raises(AttributeError):
        b58decode_int(123)


def test_decode_map_basic():
    m = _get_base58_decode_map(BITCOIN_ALPHABET, autofix=False)
    assert len(m) == 58
    assert m[ord('1')] == 0
    assert m[ord('z')] == 57
    assert ord('0') not in m
    assert ord('O') not in m
    assert ord('I') not in m
    assert ord('l') not in m


def test_decode_map_autofix_adds_aliases():
    m = _get_base58_decode_map(BITCOIN_ALPHABET, autofix=True)
    assert m[ord('0')] == m[ord('o')]
    assert m[ord('O')] == m[ord('o')]
    assert m[ord('I')] == m[ord('1')]
    assert m[ord('l')] == m[ord('1')]
    assert len(m) == 58 + 4


def test_decode_map_autofix_multiple_pivots_no_alias():
    plain = _get_base58_decode_map(NO_FIX_ALPHABET, autofix=False)
    fixed = _get_base58_decode_map(NO_FIX_ALPHABET, autofix=True)
    assert dict(plain) == dict(fixed)


def test_decode_map_autofix_zero_pivots_for_first_group():
    m = _get_base58_decode_map(NO_ZERO_GROUP_ALPHABET, autofix=True)
    assert ord('0') not in m
    assert ord('O') not in m
    assert ord('o') not in m


def test_decode_map_is_cached():
    first = _get_base58_decode_map(BITCOIN_ALPHABET, autofix=False)
    second = _get_base58_decode_map(BITCOIN_ALPHABET, autofix=False)
    assert first is second
    other = _get_base58_decode_map(BITCOIN_ALPHABET, autofix=True)
    assert other is not first


def test_b58decode_empty():
    assert b58decode(b'') == b''
    assert b58decode('') == b''


def test_b58decode_zero_values():
    assert b58decode('1') == b'\x00'
    assert b58decode(b'111') == b'\x00\x00\x00'


def test_b58decode_known_vectors():
    assert b58decode('StV1DL6CwTryKyV') == b'hello world'
    assert b58decode(b'StV1DL6CwTryKyV') == b'hello world'
    assert b58decode('2NEpo7TZRRrLZSi2U') == b'Hello World!'


def test_b58decode_leading_ones_preserved():
    assert b58decode('11StV1DL6CwTryKyV') == b'\x00\x00hello world'


def test_b58decode_strips_trailing_whitespace():
    assert b58decode('StV1DL6CwTryKyV\n') == b'hello world'
    assert b58decode(b'StV1DL6CwTryKyV  \t') == b'hello world'


def test_b58decode_ripple_alphabet_leading_symbol():
    encoded = b58encode(b'\x00\x00abc', alphabet=RIPPLE_ALPHABET)
    assert encoded.startswith(b'rr')
    assert b58decode(encoded, alphabet=RIPPLE_ALPHABET) == b'\x00\x00abc'


def test_b58decode_invalid_character():
    with pytest.raises(ValueError, match="Invalid character '0'"):
        b58decode('0abc')


def test_b58decode_invalid_character_after_leading_ones():
    with pytest.raises(ValueError, match="Invalid character 'l'"):
        b58decode('11l')


def test_b58decode_autofix():
    assert b58decode('0', autofix=True) == b58decode('o')
    assert b58decode('Il1', autofix=True) == b58decode('111')
    assert b58decode('lI1abc', autofix=True) == b58decode('111abc')


def test_b58decode_autofix_off_by_default():
    with pytest.raises(ValueError):
        b58decode('Il1')


def test_b58decode_non_ascii_raises():
    with pytest.raises(UnicodeEncodeError):
        b58decode('caf\u00e9')


def test_b58decode_invalid_type_raises():
    with pytest.raises(AttributeError):
        b58decode(123)
    with pytest.raises(AttributeError):
        b58decode(None)


@pytest.mark.parametrize(
    'data',
    [
        b'',
        b'\x00',
        b'\x00\x00',
        b'\x01',
        b'\xff',
        b'\x00\xff',
        b'\x00\x00\x00\x01',
        b'hello world',
        bytes(range(256)),
        b'\xff' * 64,
        b'\x00' * 10 + b'\x01' * 10,
        bytes(1000),
        b'\x00' + bytes(range(1, 200)),
    ],
)
@pytest.mark.parametrize('alphabet', [BITCOIN_ALPHABET, RIPPLE_ALPHABET])
def test_roundtrip(data, alphabet):
    encoded = b58encode(data, alphabet=alphabet)
    assert b58decode(encoded, alphabet=alphabet) == data


def test_roundtrip_large_integer():
    value = 2 ** 512 + 12345
    encoded = b58encode_int(value)
    assert b58decode_int(encoded) == value


@pytest.mark.parametrize('value', [0, 1, 57, 58, 255, 256, 10 ** 18, 2 ** 256])
def test_int_roundtrip(value):
    assert b58decode_int(b58encode_int(value)) == value


def test_b58encode_check_known_vector():
    data = b'\x00' * 21
    assert b58encode_check(data) == b'1111111111111111111114oLvT2'


def test_b58decode_check_known_vector():
    assert b58decode_check('1111111111111111111114oLvT2') == b'\x00' * 21
    assert b58decode_check(b'1111111111111111111114oLvT2') == b'\x00' * 21


def test_b58encode_check_appends_double_sha256_checksum():
    data = b'hello'
    digest = hashlib.sha256(hashlib.sha256(data).digest()).digest()
    assert b58encode_check(data) == b58encode(data + digest[:4])


def test_b58encode_check_str_input():
    assert b58encode_check('hello') == b58encode_check(b'hello')


def test_b58encode_check_empty():
    encoded = b58encode_check(b'')
    assert encoded
    assert b58decode_check(encoded) == b''


def test_b58encode_check_custom_alphabet():
    encoded = b58encode_check(b'hello', alphabet=RIPPLE_ALPHABET)
    assert encoded == b58encode(
        b'hello' + hashlib.sha256(hashlib.sha256(b'hello').digest()).digest()[:4],
        alphabet=RIPPLE_ALPHABET,
    )
    assert b58decode_check(encoded, alphabet=RIPPLE_ALPHABET) == b'hello'


def test_b58encode_check_non_ascii_raises():
    with pytest.raises(UnicodeEncodeError):
        b58encode_check('caf\u00e9')


def test_b58encode_check_invalid_type_raises():
    with pytest.raises(TypeError):
        b58encode_check(123)


@pytest.mark.parametrize(
    'data',
    [b'', b'\x00', b'\x00\x00abc', b'hello world', bytes(range(256)), b'\xff' * 33],
)
def test_check_roundtrip(data):
    assert b58decode_check(b58encode_check(data)) == data
    assert b58decode_check(
        b58encode_check(data, alphabet=RIPPLE_ALPHABET), alphabet=RIPPLE_ALPHABET
    ) == data


def test_b58decode_check_invalid_checksum_modified_payload():
    raw = bytearray(b58decode(b58encode_check(b'hello world')))
    raw[0] ^= 0x01
    tampered = b58encode(bytes(raw))
    with pytest.raises(ValueError, match='Invalid checksum'):
        b58decode_check(tampered)


def test_b58decode_check_invalid_checksum_modified_checksum():
    raw = bytearray(b58decode(b58encode_check(b'hello world')))
    raw[-1] ^= 0xFF
    tampered = b58encode(bytes(raw))
    with pytest.raises(ValueError, match='Invalid checksum'):
        b58decode_check(tampered)


def test_b58decode_check_empty_string_raises():
    with pytest.raises(ValueError, match='Invalid checksum'):
        b58decode_check('')


def test_b58decode_check_too_short_raises():
    with pytest.raises(ValueError, match='Invalid checksum'):
        b58decode_check('1')
    with pytest.raises(ValueError, match='Invalid checksum'):
        b58decode_check(b58encode(b'abc'))


def test_b58decode_check_invalid_character_raises():
    with pytest.raises(ValueError, match='Invalid character'):
        b58decode_check('0OIl')


def test_b58decode_check_wrong_alphabet_raises():
    encoded = b58encode_check(b'hello world')
    with pytest.raises(ValueError):
        b58decode_check(encoded, alphabet=RIPPLE_ALPHABET)


def test_b58decode_check_strips_whitespace():
    encoded = b58encode_check(b'hello world') + b'\n'
    assert b58decode_check(encoded) == b'hello world'


def test_b58decode_check_autofix():
    payload = next(
        bytes([i, i + 1, i + 2, i + 3, i + 4])
        for i in range(250)
        if b'o' in b58encode_check(bytes([i, i + 1, i + 2, i + 3, i + 4]))
    )
    encoded = b58encode_check(payload)
    broken = encoded.replace(b'o', b'0')
    with pytest.raises(ValueError, match='Invalid character'):
        b58decode_check(broken)
    assert b58decode_check(broken, autofix=True) == payload
    assert b58decode_check(encoded.replace(b'o', b'O'), autofix=True) == payload


def test_b58decode_check_autofix_one_group():
    payload = next(
        bytes([i, i + 1, i + 2, i + 3, i + 4])
        for i in range(250)
        if b'1' in b58encode_check(bytes([i, i + 1, i + 2, i + 3, i + 4])).lstrip(b'1')
    )
    encoded = b58encode_check(payload)
    stripped = encoded.lstrip(b'1')
    prefix = encoded[: len(encoded) - len(stripped)]
    broken = prefix + stripped.replace(b'1', b'l')
    assert b58decode_check(broken, autofix=True) == payload
    assert b58decode_check(prefix + stripped.replace(b'1', b'I'), autofix=True) == payload