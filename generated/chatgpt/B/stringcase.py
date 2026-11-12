import re
import pytest
import stringcase


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("", ""),
        ("hello", "hello"),
        ("Hello", "hello"),
        ("HelloWorld", "hello_world"),
        ("helloWorld", "hello_world"),
        ("hello-world", "hello_world"),
        ("hello.world", "hello_world"),
        ("hello world", "hello_world"),
        ("hello_world", "hello_world"),
        ("Hello World", "hello__world"),
        ("XMLParser", "_x_m_l_parser"),
        ("ABC", "a_b_c"),
        ("a", "a"),
        ("A", "a"),
        ("123", "123"),
        ("hello123World", "hello123_world"),
        ("foo\tbar", "foo_bar"),
        ("foo\nbar", "foo_bar"),
        ("foo--bar", "foo__bar"),
        ("foo..bar", "foo__bar"),
        ("éTest", "é_test"),
    ],
)
def test_snakecase(value, expected):
    assert stringcase.snakecase(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("", ""),
        ("hello", "hello"),
        ("HelloWorld", "hello-world"),
        ("helloWorld", "hello-world"),
        ("hello-world", "hello-world"),
        ("hello.world", "hello-world"),
        ("hello world", "hello-world"),
        ("hello_world", "hello-world"),
        ("ABC", "a-b-c"),
        ("XMLParser", "-x-m-l-parser"),
        ("a", "a"),
        ("A", "a"),
        ("123", "123"),
        ("foo\tbar", "foo-bar"),
    ],
)
def test_spinalcase(value, expected):
    assert stringcase.spinalcase(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("", ""),
        ("hello", "hello"),
        ("HelloWorld", "hello.world"),
        ("helloWorld", "hello.world"),
        ("hello-world", "hello.world"),
        ("hello_world", "hello.world"),
        ("hello world", "hello.world"),
        ("ABC", "a.b.c"),
        ("XMLParser", ".x.m.l.parser"),
        ("a", "a"),
        ("123", "123"),
    ],
)
def test_dotcase(value, expected):
    assert stringcase.dotcase(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("", ""),
        ("hello", "hello"),
        ("HelloWorld", "hello/world"),
        ("helloWorld", "hello/world"),
        ("hello-world", "hello/world"),
        ("hello.world", "hello/world"),
        ("hello world", "hello/world"),
        ("hello_world", "hello/world"),
        ("ABC", "a/b/c"),
        ("XMLParser", "/x/m/l/parser"),
        ("a", "a"),
        ("123", "123"),
    ],
)
def test_pathcase(value, expected):
    assert stringcase.pathcase(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("", ""),
        ("hello", "hello"),
        ("HelloWorld", "hello\\world"),
        ("helloWorld", "hello\\world"),
        ("hello-world", "hello\\world"),
        ("hello.world", "hello\\world"),
        ("hello world", "hello\\world"),
        ("hello_world", "hello\\world"),
        ("ABC", "a\\b\\c"),
        ("a", "a"),
        ("123", "123"),
    ],
)
def test_backslashcase(value, expected):
    assert stringcase.backslashcase(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("", ""),
        ("hello", "Hello"),
        ("hello world", "Hello world"),
        ("hello-world", "Hello-world"),
        ("hELLO", "HELLO"),
        ("a", "A"),
        ("A", "A"),
        ("123abc", "123abc"),
        ("éclair", "Éclair"),
    ],
)
def test_capitalcase(value, expected):
    assert stringcase.capitalcase(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("", ""),
        ("hello", "Hello"),
        ("hello_world", "Hello World"),
        ("hello-world", "Hello World"),
        ("hello.world", "Hello World"),
        ("hello world", "Hello World"),
        ("helloWorld", "Hello World"),
        ("HelloWorld", "Hello World"),
        ("ABC", "A B C"),
        ("a", "A"),
        ("123", "123"),
        ("foo123Bar", "Foo123 Bar"),
    ],
)
def test_titlecase(value, expected):
    assert stringcase.titlecase(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("", ""),
        ("hello", "Hello"),
        ("hello_world", "Hello world"),
        ("hello-world", "Hello world"),
        ("hello.world", "Hello world"),
        ("hello world", "Hello world"),
        ("helloWorld", "Hello world"),
        ("HelloWorld", "Hello world"),
        ("ABC", "A b c"),
        ("a", "A"),
        ("123", "123"),
        ("foo123Bar", "Foo123 bar"),
    ],
)
def test_sentencecase(value, expected):
    assert stringcase.sentencecase(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("", ""),
        ("hello", "HELLO"),
        ("Hello World", "HELLO WORLD"),
        ("hello_world", "HELLO_WORLD"),
        ("123abc", "123ABC"),
        ("éclair", "ÉCLAIR"),
        ("ß", "SS"),
    ],
)
def test_uppercase(value, expected):
    assert stringcase.uppercase(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("", ""),
        ("hello", "hello"),
        ("Hello World", "hello world"),
        ("hello_world", "hello_world"),
        ("hello-world", "hello-world"),
        ("123 abc!", "123 abc!"),
        ("a@b.com", "abcom"),
        ("foo_bar-123", "foo_bar123"),
        ("café", "café"),
        ("你好，世界", "你好世界"),
        ("a\nb", "ab"),
    ],
)
def test_lowercase(value, expected):
    assert stringcase.lowercase(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("", ""),
        (" hello ", "hello"),
        ("\tfoo\n", "foo"),
        ("   multiple   spaces   ", "multiple   spaces"),
        ("no-trimming", "no-trimming"),
        (123, "123"),
        (None, "None"),
    ],
)
def test_trimcase(value, expected):
    assert stringcase.trimcase(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("hello", "hello"),
        ("Hello World", "HelloWorld"),
        ("hello-world", "helloworld"),
        ("foo_bar", "foobar"),
        ("a@b.com", "abcom"),
        ("123!@#456", "123456"),
        ("café", "café"),
        ("你好，世界", "你好世界"),
        ("", ""),
        ("---___...", ""),
        ("a\nb", "ab"),
    ],
)
def test_alphanumcase(value, expected):
    assert stringcase.alphanumcase(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("", ""),
        ("abc", "abc"),
        ("a b", ""),
        ("a-b", ""),
        ("a.b", ""),
        ("a_b", ""),
        ("a@b", ""),
        ("123", "123"),
    ],
)
def test_camelcase_empty_or_separator_removal(value, expected):
    if expected:
        with pytest.raises(re.error):
            stringcase.camelcase(value)
    else:
        assert stringcase.camelcase(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        "hello",
        "HelloWorld",
        "hello-world",
        "hello_world",
        "hello world",
        "123abc",
        "a",
        "A",
    ],
)
def test_camelcase_raises_for_nonempty_input(value):
    with pytest.raises(re.error):
        stringcase.camelcase(value)


@pytest.mark.parametrize(
    "value",
    [
        "hello",
        "HelloWorld",
        "hello-world",
        "hello_world",
        "hello world",
        "123abc",
        "a",
        "A",
    ],
)
def test_pascalcase_raises_when_camelcase_regex_is_invalid(value):
    with pytest.raises(re.error):
        stringcase.pascalcase(value)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("", ""),
        (None, "none"),
        (123, "123"),
        (True, "true"),
        (["A", "B"], "['a', 'b']"),
    ],
)
def test_lowercase_converts_values_to_strings(value, expected):
    assert stringcase.lowercase(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("", ""),
        (None, "NONE"),
        (123, "123"),
        (True, "TRUE"),
        (["a", "b"], "['A', 'B']"),
    ],
)
def test_uppercase_converts_values_to_strings(value, expected):
    assert stringcase.uppercase(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, "None"),
        (123, "123"),
        (True, "True"),
        (["a", "b"], "['a', 'b']"),
    ],
)
def test_capitalcase_converts_values_to_strings(value, expected):
    assert stringcase.capitalcase(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, "none"),
        (123, "123"),
        (True, "true"),
        (["a", "b"], "['a', 'b']"),
    ],
)
def test_snakecase_converts_values_to_strings(value, expected):
    assert stringcase.snakecase(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("  Hello World  ", "  Hello World  "),
        ("", ""),
        ("foo\nbar", "foo\nbar"),
    ],
)
def test_trimcase_preserves_non_whitespace_content(value, expected):
    assert stringcase.trimcase(value) == expected


def test_constcase_converts_snakecase_to_uppercase():
    assert stringcase.constcase("helloWorld") == "HELLO_WORLD"
    assert stringcase.constcase("hello-world") == "HELLO_WORLD"
    assert stringcase.constcase("hello world") == "HELLO_WORLD"
    assert stringcase.constcase("") == ""


def test_constcase_handles_acronyms():
    assert stringcase.constcase("XMLParser") == "_X_M_L_PARSER"


def test_titlecase_preserves_empty_components():
    assert stringcase.titlecase("_hello_") == " Hello "


def test_sentencecase_collapses_punctuation_to_spaces():
    assert stringcase.sentencecase("hello---world") == "Hello   world"


def test_sentencecase_handles_leading_and_trailing_whitespace():
    assert stringcase.sentencecase("  hello  ") == "Hello"


def test_pathcase_handles_repeated_punctuation():
    assert stringcase.pathcase("foo--bar..baz") == "foo__bar__baz"


def test_backslashcase_handles_repeated_punctuation():
    assert stringcase.backslashcase("foo--bar..baz") == "foo\\\\bar\\\\baz"


def test_alphanumcase_rejects_non_string_input():
    with pytest.raises(TypeError):
        stringcase.alphanumcase(123)


def test_alphanumcase_rejects_none():
    with pytest.raises(TypeError):
        stringcase.alphanumcase(None)


def test_all_string_converters_handle_empty_strings():
    assert stringcase.snakecase("") == ""
    assert stringcase.spinalcase("") == ""
    assert stringcase.dotcase("") == ""
    assert stringcase.pathcase("") == ""
    assert stringcase.backslashcase("") == ""
    assert stringcase.sentencecase("") == ""
    assert stringcase.titlecase("") == ""
    assert stringcase.constcase("") == ""
    assert stringcase.capitalcase("") == ""
    assert stringcase.camelcase("") == ""
    assert stringcase.pascalcase("") == ""


def test_case_converters_handle_numeric_strings():
    assert stringcase.snakecase("12345") == "12345"
    assert stringcase.spinalcase("12345") == "12345"
    assert stringcase.dotcase("12345") == "12345"
    assert stringcase.pathcase("12345") == "12345"
    assert stringcase.backslashcase("12345") == "12345"
    assert stringcase.titlecase("12345") == "12345"
    assert stringcase.sentencecase("12345") == "12345"
    assert stringcase.constcase("12345") == "12345"


def test_unicode_case_conversion():
    assert stringcase.lowercase("ÄÖÜ") == "äöü"
    assert stringcase.uppercase("äöü") == "ÄÖÜ"
    assert stringcase.capitalcase("äbc") == "Äbc"
    assert stringcase.alphanumcase("café") == "café"


def test_snakecase_only_inserts_underscores_before_ascii_uppercase():
    assert stringcase.snakecase("éABC") == "é_a_b_c"
    assert stringcase.snakecase("abcÉdef") == "abcÉdef"


def test_sentencecase_handles_acronyms():
    assert stringcase.sentencecase("XMLParser") == "X m l parser"


def test_titlecase_handles_acronyms():
    assert stringcase.titlecase("XMLParser") == "X M L Parser"


def test_constcase_handles_non_ascii_characters():
    assert stringcase.constcase("café au lait") == "CAFÉ_AU_LAIT"