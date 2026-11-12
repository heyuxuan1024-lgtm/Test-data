import pytest

from stdnum import isbn
from stdnum.exceptions import (
    InvalidChecksum,
    InvalidComponent,
    InvalidFormat,
    InvalidLength,
    ValidationError,
)


class TestCompact:
    def test_strips_hyphens(self):
        assert isbn.compact('1-85798-218-5') == '1857982185'

    def test_strips_spaces(self):
        assert isbn.compact('1 85798 218 5') == '1857982185'

    def test_strips_surrounding_whitespace(self):
        assert isbn.compact('  1857982185  ') == '1857982185'

    def test_uppercases_x(self):
        assert isbn.compact('080442957x') == '080442957X'

    def test_nine_digits_padded_with_zero(self):
        assert isbn.compact('80442957X') == '080442957X'

    def test_nine_digit_numeric_padded(self):
        assert isbn.compact('185798218') == '0185798218'

    def test_isbn13_unchanged(self):
        assert isbn.compact('978-9024538270') == '9789024538270'

    def test_convert_isbn10_to_isbn13(self):
        assert isbn.compact('1-85798-218-5', convert=True) == '9781857982183'

    def test_convert_isbn13_stays_isbn13(self):
        assert isbn.compact('978-9024538270', convert=True) == '9789024538270'

    def test_convert_nine_digits(self):
        assert isbn.compact('80442957X', convert=True) == '9780804429573'

    def test_empty_string(self):
        assert isbn.compact('') == ''

    def test_other_lengths_unchanged(self):
        assert isbn.compact('12345') == '12345'


class TestCalcCheckDigit:
    def test_numeric_check_digit(self):
        assert isbn._calc_isbn10_check_digit('185798218') == '5'

    def test_x_check_digit(self):
        assert isbn._calc_isbn10_check_digit('080442957') == 'X'

    def test_zero_check_digit(self):
        assert isbn._calc_isbn10_check_digit('000000000') == '0'

    def test_returns_string(self):
        assert isinstance(isbn._calc_isbn10_check_digit('123456789'), str)

    def test_non_digit_raises_value_error(self):
        with pytest.raises(ValueError):
            isbn._calc_isbn10_check_digit('12345678a')


class TestValidate:
    def test_valid_isbn13(self):
        assert isbn.validate('978-9024538270') == '9789024538270'

    def test_valid_isbn13_979(self):
        assert isbn.validate('9791090636071') == '9791090636071'

    def test_valid_isbn10(self):
        assert isbn.validate('1-85798-218-5') == '1857982185'

    def test_valid_isbn10_with_x(self):
        assert isbn.validate('0-8044-2957-X') == '080442957X'

    def test_valid_isbn10_lowercase_x(self):
        assert isbn.validate('080442957x') == '080442957X'

    def test_valid_nine_digit(self):
        assert isbn.validate('80442957X') == '080442957X'

    def test_convert_isbn10(self):
        assert isbn.validate('1-85798-218-5', convert=True) == '9781857982183'

    def test_convert_isbn13(self):
        assert isbn.validate('978-9024538270', convert=True) == '9789024538270'

    def test_invalid_checksum_isbn10(self):
        with pytest.raises(InvalidChecksum):
            isbn.validate('1857982186')

    def test_invalid_checksum_isbn13(self):
        with pytest.raises(InvalidChecksum):
            isbn.validate('978-9024538271')

    def test_invalid_component_prefix(self):
        with pytest.raises(InvalidComponent):
            isbn.validate('9771234567003')

    def test_invalid_format_letters_in_body(self):
        with pytest.raises(InvalidFormat):
            isbn.validate('18579A2185')

    def test_invalid_format_letters_isbn13(self):
        with pytest.raises(InvalidFormat):
            isbn.validate('97890245A8270')

    def test_invalid_length_short(self):
        with pytest.raises(InvalidLength):
            isbn.validate('12345')

    def test_invalid_length_eleven(self):
        with pytest.raises(InvalidLength):
            isbn.validate('18579821851')

    def test_invalid_length_fourteen(self):
        with pytest.raises(InvalidLength):
            isbn.validate('97890245382701')

    def test_invalid_length_twelve(self):
        with pytest.raises(InvalidLength):
            isbn.validate('978902453827')

    def test_empty_string(self):
        with pytest.raises(ValidationError):
            isbn.validate('')

    def test_exceptions_are_validation_errors(self):
        with pytest.raises(ValidationError):
            isbn.validate('1857982186')

    def test_non_string_raises(self):
        with pytest.raises((TypeError, AttributeError)):
            isbn.validate(None)


class TestIsbnType:
    def test_isbn10(self):
        assert isbn.isbn_type('1-85798-218-5') == 'ISBN10'

    def test_isbn13(self):
        assert isbn.isbn_type('978-0-471-11709-4') == 'ISBN13'

    def test_invalid_checksum(self):
        assert isbn.isbn_type('1857982186') is None

    def test_invalid_length(self):
        assert isbn.isbn_type('123') is None

    def test_invalid_format(self):
        assert isbn.isbn_type('abcdefghij') is None

    def test_empty(self):
        assert isbn.isbn_type('') is None

    def test_nine_digit_is_isbn10(self):
        assert isbn.isbn_type('80442957X') == 'ISBN10'


class TestIsValid:
    def test_valid_isbn10(self):
        assert isbn.is_valid('1-85798-218-5') is True

    def test_valid_isbn13(self):
        assert isbn.is_valid('978-9024538270') is True

    def test_invalid_checksum(self):
        assert isbn.is_valid('978-9024538271') is False

    def test_invalid_length(self):
        assert isbn.is_valid('12') is False

    def test_invalid_format(self):
        assert isbn.is_valid('18579A2185') is False

    def test_invalid_component(self):
        assert isbn.is_valid('9771234567003') is False

    def test_empty(self):
        assert isbn.is_valid('') is False


class TestToIsbn13:
    def test_from_isbn10_plain(self):
        assert isbn.to_isbn13('1857982185') == '9781857982183'

    def test_from_isbn10_hyphens(self):
        assert isbn.to_isbn13('1-85798-218-5') == '978-1-85798-218-3'

    def test_from_isbn10_spaces(self):
        assert isbn.to_isbn13('1 85798 218 5') == '978 1 85798 218 3'

    def test_already_isbn13_unchanged(self):
        assert isbn.to_isbn13('978-1-85798-218-3') == '978-1-85798-218-3'

    def test_already_isbn13_plain(self):
        assert isbn.to_isbn13('9781857982183') == '9781857982183'

    def test_isbn13_surrounding_whitespace_stripped(self):
        assert isbn.to_isbn13('  9781857982183  ') == '9781857982183'

    def test_isbn10_with_x(self):
        assert isbn.to_isbn13('080442957X') == '9780804429573'

    def test_nine_digit_plain(self):
        assert isbn.to_isbn13('80442957X') == '9780804429573'

    def test_nine_digit_hyphens(self):
        assert isbn.to_isbn13('8-04429-57X') == '978-08-04429-573'

    def test_roundtrip_validates(self):
        assert isbn.is_valid(isbn.to_isbn13('0-8044-2957-X'))


class TestToIsbn10:
    def test_from_isbn13_hyphens(self):
        assert isbn.to_isbn10('978-1-85798-218-3') == '1-85798-218-5'

    def test_from_isbn13_plain(self):
        assert isbn.to_isbn10('9781857982183') == '1857982185'

    def test_from_isbn13_spaces(self):
        assert isbn.to_isbn10('978 1 85798 218 3') == '1 85798 218 5'

    def test_already_isbn10_unchanged(self):
        assert isbn.to_isbn10('1-85798-218-5') == '1-85798-218-5'

    def test_already_isbn10_plain(self):
        assert isbn.to_isbn10('1857982185') == '1857982185'

    def test_surrounding_whitespace_stripped(self):
        assert isbn.to_isbn10('  9781857982183  ') == '1857982185'

    def test_x_check_digit(self):
        assert isbn.to_isbn10('9780804429573') == '080442957X'

    def test_979_prefix_raises_invalid_component(self):
        with pytest.raises(InvalidComponent):
            isbn.to_isbn10('9791090636071')

    def test_invalid_isbn13_raises_invalid_format(self):
        with pytest.raises(InvalidFormat):
            isbn.to_isbn10('9781857982184')

    def test_garbage_raises_invalid_format(self):
        with pytest.raises(InvalidFormat):
            isbn.to_isbn10('12345')

    def test_empty_raises_invalid_format(self):
        with pytest.raises(InvalidFormat):
            isbn.to_isbn10('')

    def test_roundtrip(self):
        assert isbn.to_isbn10(isbn.to_isbn13('1-85798-218-5')) == '1-85798-218-5'


class TestSplit:
    def test_isbn13(self):
        assert isbn.split('9780471117094') == ('978', '0', '471', '11709', '4')

    def test_isbn10_has_empty_prefix(self):
        assert isbn.split('1857982185') == ('', '1', '85798', '218', '5')

    def test_isbn10_convert(self):
        assert isbn.split('1857982185', convert=True) == ('978', '1', '85798', '218', '3')

    def test_with_separators(self):
        assert isbn.split('978-0-471-11709-4') == ('978', '0', '471', '11709', '4')

    def test_returns_five_tuple(self):
        result = isbn.split('9780471117094')
        assert isinstance(result, tuple)
        assert len(result) == 5

    def test_check_digit_is_last_char(self):
        assert isbn.split('080442957X')[-1] == 'X'

    def test_nine_digit_input(self):
        result = isbn.split('80442957X')
        assert result[0] == ''
        assert result[-1] == 'X'

    def test_unknown_range_has_empty_components(self):
        result = isbn.split('9780000000002')
        assert len(result) == 5
        assert result[-1] == '2'

    def test_empty_string_does_not_crash_or_raises_cleanly(self):
        try:
            result = isbn.split('')
        except (ValidationError, IndexError):
            return
        assert len(result) == 5


class TestFormat:
    def test_isbn13_default(self):
        assert isbn.format('9780471117094') == '978-0-471-11709-4'

    def test_isbn10_default(self):
        assert isbn.format('1857982185') == '1-85798-218-5'

    def test_custom_separator(self):
        assert isbn.format('9780471117094', separator=' ') == '978 0 471 11709 4'

    def test_isbn10_convert(self):
        assert isbn.format('1857982185', convert=True) == '978-1-85798-218-3'

    def test_empty_separator_equals_compact(self):
        assert isbn.format('9780471117094', separator='') == isbn.compact('9780471117094')

    def test_isbn10_empty_separator(self):
        assert isbn.format('1857982185', separator='') == '1857982185'

    def test_reformat_already_formatted(self):
        assert isbn.format('978-0-471-11709-4') == '978-0-471-11709-4'

    def test_multichar_separator(self):
        assert isbn.format('1857982185', separator='--') == '1--85798--218--5'

    def test_isbn10_with_x(self):
        assert isbn.format('080442957X').endswith('-X')

    def test_unknown_range_skips_empty_parts(self):
        result = isbn.format('9780000000002')
        assert '--' not in result
        assert result.replace('-', '') == '9780000000002'