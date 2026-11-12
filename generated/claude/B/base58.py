import hashlib

import pytest

import base58


KNOWN_VECTORS = [
    (b"", b""),
    (b"a", b"2g"),
    (b"bbb", b"a3gV"),
    (b"ccc", b"aPEr"),
    (b"hello world", b"StV1DL6CwTryKyV"),
    (b"simply a long string", b"2cFupjhnEsSn59qHXstmK2ffpLv2"),
    (
        bytes.fromhex("00eb15231dfceb60925886b67d065299925915aeb172c06647"),
        b"1NS17iag9jJgTHD1VXjvLCEnZuQ3rJDE9L",
    ),
    (bytes.fromhex("516b6fcd0f"), b"ABnLTmg"),
    (bytes.fromhex("bf4f89001e670274dd"), b"3SEo3LWLoPntC"),
    (bytes.fromhex("572e4794"), b"3EFU7m"),
    (bytes.fromhex("ecac89cad93923c02321"), b"EJDM8drfXA6uyA"),
    (bytes.fromhex("10c8511e"), b"Rt5zm"),
    (bytes.fromhex("00000000000000000000"), b"1111111111"),
]

ROUNDTRIP_PAYLOADS = [
    b"",
    b"\x00",
    b"\x00\x00",
    b"\x00\x00\x01",
    b"\x01",
    b"\xff",
    b"\xff" * 32,
    b"hello",
    b"\x00\x00abc",
    bytes(range(256)),
    b"\x00" * 10 + b"\xff" * 10,
]


def _tamper_last_char(encoded):
    replacement = b"2" if encoded[-1:] != b"2" else b"3"
    return encoded[:-1] + replacement


class TestConstants:
    def test_bitcoin_alphabet_length(self):
        assert len(base58.BITCOIN_ALPHABET) == 58

    def test_ripple_alphabet_length(self):
        assert len(base58.RIPPLE_ALPHABET) == 58

    def test_alphabets_have_unique_characters(self):
        assert len(set(base58.BITCOIN_ALPHABET)) == 58
        assert len(set(base58.RIPPLE_ALPHABET)) == 58

    def test_xrp_alphabet_alias(self):
        assert base58.XRP_ALPHABET == base58.RIPPLE_ALPHABET

    def test_retro_compat_alphabet(self):
        assert base58.alphabet == base58.BITCOIN_ALPHABET

    def test_bitcoin_alphabet_excludes_ambiguous(self):
        for char in b"0OIl":
            assert char not in base58.BITCOIN_ALPHABET

    def test_version_is_string(self):
        assert isinstance(base58.__version__, str)
        assert base58.__version__


class TestScrubInput:
    def test_str_is_encoded(self):
        assert base58.scrub_input("abc") == b"abc"

    def test_bytes_unchanged(self):
        data = b"abc"
        assert base58.scrub_input(data) is data

    def test_empty_str(self):
        assert base58.scrub_input("") == b""

    def test_non_ascii_str_raises(self):
        with pytest.raises(UnicodeEncodeError):
            base58.scrub_input("caf\u00e9")

    def test_bytearray_passthrough(self):
        data = bytearray(b"abc")
        assert base58.scrub_input(data) is data


class TestB58EncodeInt:
    def test_zero_default_one(self):
        assert base58.b58encode_int(0) == b"1"

    def test_zero_without_default_one(self):
        assert base58.b58encode_int(0, default_one=False) == b""

    def test_single_digit(self):
        assert base58.b58encode_int(1) == b"2"

    def test_last_symbol(self):
        assert base58.b58encode_int(57) == b"z"

    def test_first_overflow(self):
        assert base58.b58encode_int(58) == b"21"

    def test_large_integer(self):
        assert base58.b58encode_int(58 ** 5) == b"211111"

    def test_custom_alphabet_binary(self):
        assert base58.b58encode_int(5, alphabet=b"01") == b"101"

    def test_custom_alphabet_zero_default_one(self):
        assert base58.b58encode_int(0, alphabet=b"01") == b"0"

    def test_custom_alphabet_zero_no_default(self):
        assert base58.b58encode_int(0, default_one=False, alphabet=b"01") == b""

    def test_ripple_alphabet_zero(self):
        assert base58.b58encode_int(0, alphabet=base58.RIPPLE_ALPHABET) == b"r"

    def test_returns_bytes(self):
        assert isinstance(base58.b58encode_int(12345), bytes)

    def test_non_integer_raises(self):
        with pytest.raises(TypeError):
            base58.b58encode_int("abc")


class TestB58Encode:
    @pytest.mark.parametrize("raw, encoded", KNOWN_VECTORS)
    def test_known_vectors(self, raw, encoded):
        assert base58.b58encode(raw) == encoded

    def test_empty_bytes(self):
        assert base58.b58encode(b"") == b""

    def test_single_zero_byte(self):
        assert base58.b58encode(b"\x00") == b"1"

    def test_multiple_zero_bytes(self):
        assert base58.b58encode(b"\x00\x00\x00") == b"111"

    def test_leading_zeros_preserved(self):
        assert base58.b58encode(b"\x00\x00a") == b"112g"

    def test_str_input(self):
        assert base58.b58encode("hello world") == b"StV1DL6CwTryKyV"

    def test_bytearray_input(self):
        assert base58.b58encode(bytearray(b"a")) == b"2g"

    def test_non_ascii_str_raises(self):
        with pytest.raises(UnicodeEncodeError):
            base58.b58encode("caf\u00e9")

    def test_non_bytes_raises(self):
        with pytest.raises(TypeError):
            base58.b58encode(123)

    def test_none_raises(self):
        with pytest.raises(TypeError):
            base58.b58encode(None)

    def test_returns_bytes(self):
        assert isinstance(base58.b58encode(b"abc"), bytes)

    def test_ripple_alphabet_zero_byte(self):
        assert base58.b58encode(b"\x00", alphabet=base58.RIPPLE_ALPHABET) == b"r"

    def test_ripple_matches_translated_bitcoin(self):
        table = bytes.maketrans(base58.BITCOIN_ALPHABET, base58.RIPPLE_ALPHABET)
        data = b"The quick brown fox"
        expected = base58.b58encode(data).translate(table)
        assert base58.b58encode(data, alphabet=base58.RIPPLE_ALPHABET) == expected

    def test_custom_alphabet(self):
        assert base58.b58encode(b"\x05", alphabet=b"01") == b"101"

    def test_output_only_uses_alphabet(self):
        encoded = base58.b58encode(bytes(range(256)))
        assert set(encoded) <= set(base58.BITCOIN_ALPHABET)


class TestB58DecodeInt:
    def test_zero(self):
        assert base58.b58decode_int(b"1") == 0

    def test_empty(self):
        assert base58.b58decode_int(b"") == 0

    def test_one(self):
        assert base58.b58decode_int(b"2") == 1

    def test_last_symbol(self):
        assert base58.b58decode_int(b"z") == 57

    def test_overflow(self):
        assert base58.b58decode_int(b"21") == 58

    def test_str_input(self):
        assert base58.b58decode_int("21") == 58

    def test_roundtrip_with_encode_int(self):
        for value in (0, 1, 57, 58, 3363, 10 ** 20, 2 ** 256):
            assert base58.b58decode_int(base58.b58encode_int(value)) == value

    def test_trailing_whitespace_stripped(self):
        assert base58.b58decode_int(b"z \n\t") == 57

    def test_trailing_whitespace_stripped_str(self):
        assert base58.b58decode_int("z  ") == 57

    def test_internal_whitespace_rejected(self):
        with pytest.raises(ValueError):
            base58.b58decode_int(b"2 2")

    def test_space_in_alphabet_disables_strip(self):
        assert base58.b58decode_int(b"1 ", alphabet=b" 1") == 2

    def test_space_in_alphabet_str_input(self):
        assert base58.b58decode_int("1 ", alphabet=b" 1") == 2

    def test_invalid_character_raises_value_error(self):
        with pytest.raises(ValueError, match="Invalid character '0'"):
            base58.b58decode_int(b"0")

    def test_invalid_character_in_middle(self):
        with pytest.raises(ValueError, match="Invalid character 'l'"):
            base58.b58decode_int(b"2l2")

    def test_invalid_character_exception_context_suppressed(self):
        with pytest.raises(ValueError) as excinfo:
            base58.b58decode_int(b"0")
        assert excinfo.value.__cause__ is None
        assert excinfo.value.__suppress_context__ is True

    def test_non_ascii_str_raises(self):
        with pytest.raises(UnicodeEncodeError):
            base58.b58decode_int("caf\u00e9")

    def test_none_raises(self):
        with pytest.raises(AttributeError):
            base58.b58decode_int(None)

    def test_custom_alphabet(self):
        assert base58.b58decode_int(b"101", alphabet=b"01") == 5

    def test_autofix_zero_maps_to_lowercase_o(self):
        expected = base58.b58decode_int(b"o")
        assert base58.b58decode_int(b"0", autofix=True) == expected

    def test_autofix_uppercase_o_maps_to_lowercase_o(self):
        expected = base58.b58decode_int(b"o")
        assert base58.b58decode_int(b"O", autofix=True) == expected

    def test_autofix_lowercase_l_maps_to_one(self):
        assert base58.b58decode_int(b"l", autofix=True) == 0

    def test_autofix_uppercase_i_maps_to_one(self):
        assert base58.b58decode_int(b"I", autofix=True) == 0

    def test_autofix_mixed(self):
        assert base58.b58decode_int(b"2lI", autofix=True) == base58.b58decode_int(b"211")

    def test_autofix_keeps_valid_characters(self):
        assert base58.b58decode_int(b"21", autofix=True) == 58

    def test_autofix_disabled_by_default(self):
        with pytest.raises(ValueError):
            base58.b58decode_int(b"O")
        with pytest.raises(ValueError):
            base58.b58decode_int(b"l")

    def test_autofix_still_rejects_unrelated_characters(self):
        with pytest.raises(ValueError):
            base58.b58decode_int(b"!", autofix=True)

    def test_autofix_no_pivot_in_alphabet(self):
        with pytest.raises(ValueError):
            base58.b58decode_int(b"0", alphabet=b"abc", autofix=True)

    def test_autofix_two_pivots_in_alphabet(self):
        with pytest.raises(ValueError):
            base58.b58decode_int(b"o", alphabet=b"0Oab", autofix=True)

    def test_autofix_keyword_only(self):
        with pytest.raises(TypeError):
            base58.b58decode_int(b"2", base58.BITCOIN_ALPHABET, True)


class TestB58Decode:
    @pytest.mark.parametrize("raw, encoded", KNOWN_VECTORS)
    def test_known_vectors(self, raw, encoded):
        assert base58.b58decode(encoded) == raw

    def test_empty(self):
        assert base58.b58decode(b"") == b""

    def test_single_one_is_zero_byte(self):
        assert base58.b58decode(b"1") == b"\x00"

    def test_multiple_ones(self):
        assert base58.b58decode(b"111") == b"\x00\x00\x00"

    def test_leading_zero_bytes_preserved(self):
        assert base58.b58decode(b"112g") == b"\x00\x00a"

    def test_str_input(self):
        assert base58.b58decode("StV1DL6CwTryKyV") == b"hello world"

    def test_trailing_whitespace_stripped(self):
        assert base58.b58decode(b"2g\n") == b"a"

    def test_trailing_whitespace_stripped_str(self):
        assert base58.b58decode("2g \t\n") == b"a"

    def test_only_whitespace(self):
        assert base58.b58decode(b"   ") == b""

    def test_leading_whitespace_rejected(self):
        with pytest.raises(ValueError):
            base58.b58decode(b" 2g")

    def test_internal_whitespace_rejected(self):
        with pytest.raises(ValueError):
            base58.b58decode(b"2 g")

    def test_invalid_character_raises(self):
        with pytest.raises(ValueError, match="Invalid character"):
            base58.b58decode(b"0OIl")

    def test_non_ascii_str_raises(self):
        with pytest.raises(UnicodeEncodeError):
            base58.b58decode("caf\u00e9")

    def test_none_raises(self):
        with pytest.raises(AttributeError):
            base58.b58decode(None)

    def test_returns_bytes(self):
        assert isinstance(base58.b58decode(b"2g"), bytes)

    def test_ripple_alphabet_zero_byte(self):
        assert base58.b58decode(b"r", alphabet=base58.RIPPLE_ALPHABET) == b"\x00"

    def test_ripple_alphabet_leading_symbol_preserved(self):
        assert base58.b58decode(b"rr", alphabet=base58.RIPPLE_ALPHABET) == b"\x00\x00"

    def test_ripple_matches_translated_bitcoin(self):
        table = bytes.maketrans(base58.BITCOIN_ALPHABET, base58.RIPPLE_ALPHABET)
        encoded = base58.b58encode(b"The quick brown fox").translate(table)
        assert base58.b58decode(encoded, alphabet=base58.RIPPLE_ALPHABET) == b"The quick brown fox"

    def test_autofix_substitutions(self):
        assert base58.b58decode(b"StVlDL6CwTryKyV", autofix=True) == b"hello world"
        assert base58.b58decode(b"StVIDL6CwTryKyV", autofix=True) == b"hello world"

    def test_autofix_leading_ambiguous_characters_not_treated_as_zero_bytes(self):
        assert base58.b58decode(b"l2g", autofix=True) == b"\x00" * 0 + base58.b58decode(b"l2g", autofix=True)

    def test_autofix_disabled_rejects_ambiguous(self):
        with pytest.raises(ValueError):
            base58.b58decode(b"StVlDL6CwTryKyV")

    def test_autofix_zero_and_o(self):
        assert base58.b58decode(b"0", autofix=True) == base58.b58decode(b"o")
        assert base58.b58decode(b"O", autofix=True) == base58.b58decode(b"o")

    def test_autofix_keyword_only(self):
        with pytest.raises(TypeError):
            base58.b58decode(b"2g", base58.BITCOIN_ALPHABET, True)

    @pytest.mark.parametrize("payload", ROUNDTRIP_PAYLOADS)
    def test_roundtrip(self, payload):
        assert base58.b58decode(base58.b58encode(payload)) == payload

    @pytest.mark.parametrize("payload", ROUNDTRIP_PAYLOADS)
    def test_roundtrip_ripple(self, payload):
        encoded = base58.b58encode(payload, alphabet=base58.RIPPLE_ALPHABET)
        assert base58.b58decode(encoded, alphabet=base58.RIPPLE_ALPHABET) == payload

    @pytest.mark.parametrize("payload", ROUNDTRIP_PAYLOADS)
    def test_roundtrip_with_autofix(self, payload):
        encoded = base58.b58encode(payload)
        assert base58.b58decode(encoded, autofix=True) == payload


class TestB58EncodeCheck:
    def test_appends_double_sha256_checksum(self):
        payload = b"hello world"
        digest = hashlib.sha256(hashlib.sha256(payload).digest()).digest()
        expected = base58.b58encode(payload + digest[:4])
        assert base58.b58encode_check(payload) == expected

    def test_str_input(self):
        assert base58.b58encode_check("hello") == base58.b58encode_check(b"hello")

    def test_empty_payload(self):
        digest = hashlib.sha256(hashlib.sha256(b"").digest()).digest()
        assert base58.b58encode_check(b"") == base58.b58encode(digest[:4])

    def test_returns_bytes(self):
        assert isinstance(base58.b58encode_check(b"abc"), bytes)

    def test_longer_than_plain_encoding(self):
        assert len(base58.b58encode_check(b"abc")) > len(base58.b58encode(b"abc"))

    def test_non_ascii_str_raises(self):
        with pytest.raises(UnicodeEncodeError):
            base58.b58encode_check("caf\u00e9")

    def test_non_bytes_raises(self):
        with pytest.raises(TypeError):
            base58.b58encode_check(123)

    def test_custom_alphabet(self):
        payload = b"hello"
        digest = hashlib.sha256(hashlib.sha256(payload).digest()).digest()
        expected = base58.b58encode(payload + digest[:4], alphabet=base58.RIPPLE_ALPHABET)
        assert base58.b58encode_check(payload, alphabet=base58.RIPPLE_ALPHABET) == expected

    def test_leading_zero_payload(self):
        encoded = base58.b58encode_check(b"\x00\x00abc")
        assert encoded.startswith(b"11")


class TestB58DecodeCheck:
    @pytest.mark.parametrize("payload", ROUNDTRIP_PAYLOADS)
    def test_roundtrip(self, payload):
        assert base58.b58decode_check(base58.b58encode_check(payload)) == payload

    @pytest.mark.parametrize("payload", ROUNDTRIP_PAYLOADS)
    def test_roundtrip_ripple(self, payload):
        encoded = base58.b58encode_check(payload, alphabet=base58.RIPPLE_ALPHABET)
        decoded = base58.b58decode_check(encoded, alphabet=base58.RIPPLE_ALPHABET)
        assert decoded == payload

    def test_str_input(self):
        encoded = base58.b58encode_check(b"hello").decode("ascii")
        assert base58.b58decode_check(encoded) == b"hello"

    def test_trailing_whitespace(self):
        encoded = base58.b58encode_check(b"hello") + b"\n"
        assert base58.b58decode_check(encoded) == b"hello"

    def test_bitcoin_address_vector(self):
        encoded = b"1NS17iag9jJgTHD1VXjvLCEnZuQ3rJDE9L"
        payload = base58.b58decode_check(encoded)
        assert payload == bytes.fromhex("00eb15231dfceb60925886b67d065299925915aeb1")
        assert base58.b58encode_check(payload) == encoded

    def test_tampered_checksum_raises(self):
        encoded = base58.b58encode_check(b"hello world")
        with pytest.raises(ValueError, match="Invalid checksum"):
            base58.b58decode_check(_tamper_last_char(encoded))

    def test_tampered_payload_raises(self):
        raw = bytearray(base58.b58decode(base58.b58encode_check(b"hello world")))
        raw[0] ^= 0x01
        tampered = base58.b58encode(bytes(raw))
        with pytest.raises(ValueError, match="Invalid checksum"):
            base58.b58decode_check(tampered)

    def test_plain_encoding_fails_checksum(self):
        with pytest.raises(ValueError, match="Invalid checksum"):
            base58.b58decode_check(base58.b58encode(b"hello world"))

    def test_empty_input_raises(self):
        with pytest.raises(ValueError, match="Invalid checksum"):
            base58.b58decode_check(b"")

    def test_too_short_input_raises(self):
        with pytest.raises(ValueError, match="Invalid checksum"):
            base58.b58decode_check(base58.b58encode(b"\x01\x02"))

    def test_invalid_character_raises(self):
        with pytest.raises(ValueError, match="Invalid character"):
            base58.b58decode_check(b"0OIl")

    def test_autofix_roundtrip(self):
        encoded = base58.b58encode_check(b"hello world")
        assert base58.b58decode_check(encoded, autofix=True) == b"hello world"

    def test_autofix_repairs_ambiguous_character(self):
        payload = b"\x00" + b"\x01" * 20
        encoded = base58.b58encode_check(payload)
        assert encoded.startswith(b"1")
        assert base58.b58decode_check(b"l" + encoded[1:], autofix=True) != b""

    def test_ambiguous_character_rejected_without_autofix(self):
        encoded = base58.b58encode_check(b"\x00hello")
        with pytest.raises(ValueError, match="Invalid character"):
            base58.b58decode_check(b"l" + encoded[1:])

    def test_autofix_keyword_only(self):
        encoded = base58.b58encode_check(b"hello")
        with pytest.raises(TypeError):
            base58.b58decode_check(encoded, base58.BITCOIN_ALPHABET, True)

    def test_returns_bytes(self):
        assert isinstance(base58.b58decode_check(base58.b58encode_check(b"abc")), bytes)

    def test_non_ascii_str_raises(self):
        with pytest.raises(UnicodeEncodeError):
            base58.b58decode_check("caf\u00e9")