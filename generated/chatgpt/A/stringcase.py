
import pytest
import stringcase as module


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("hello", "hello"),
        ("Hello", "hello"),
        ("", ""),
        ("123", "123"),
        ("ABC", "abc"),
        ("a_b", "a_b"),
        ("hello-world", "hellorld"),
        ("hello world", "hellorld"),
        ("hello.world", "hellorld"),
        (None, "none"),
        (123, "123"),
        (True, "true"),
    ],
)
def test_camelcase(value, expected):
    assert module.camelcase(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("hello", "Hello"),
        ("Hello", "Hello"),
        ("", ""),
        ("hELLO", "HELLO"),
        ("123abc", "123abc"),
        ("hello world", "hello world"),
        (None, "None"),
        (123, "123"),
        (True, "True"),
    ],
)
def test_capitalcase(value, expected):
    assert module.capitalcase(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("hello", "HELLO"),
        ("HelloWorld", "HELLO_WORLD"),
        ("hello-world", "HELLO_WORLD"),
        ("hello.world", "HELLO_WORLD"),
        ("hello world", "HELLO_WORLD"),
        ("", ""),
        ("ABC", "A_B_C"),
        ("already_snake", "ALREADY_SNAKE"),
        ("one--two", "ONE__TWO"),
        (123, "123"),
        (None, "NONE"),
    ],
)
def test_constcase(value, expected):
    assert module.constcase(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("HELLO", "hello"),
        ("Hello World", "hello world"),
        ("", ""),
        ("123ABC", "123abc"),
        (None, "none"),
        (123, "123"),
        (True, "true"),
    ],
)
def test_lowercase(value, expected):
    assert module.lowercase(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("hello", "Hello"),
        ("Hello", "Hello"),
        ("", ""),
        ("hello-world", "Hellorld"),
        ("hello world", "Hellorld"),
        ("hello.world", "Hellorld"),
        ("ABC", "A_B_C"),
        (123, "123"),
        (None, "None"),
    ],
)
def test_pascalcase(value, expected):
    assert module.pascalcase(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("hello", "hello"),
        ("HelloWorld", "hello/world"),
        ("hello-world", "hello/world"),
        ("hello.world", "hello/world"),
        ("hello world", "hello/world"),
        ("", ""),
        ("already_snake", "already/snake"),
        ("one--two", "one//two"),
        ("ABC", "a/b/c"),
        (123, "123"),
        (None, "none"),
    ],
)
def test_pathcase(value, expected):
    assert module.pathcase(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("hello", "hello"),
        ("HelloWorld", "hello\\world"),
        ("hello-world", "hello\\world"),
        ("hello.world", "hello\\world"),
        ("hello world", "hello\\world"),
        ("", ""),
        ("already_snake", "already\\snake"),
        ("one--two", "one\\\\two"),
        ("ABC", "a\\b\\c"),
        (123, "123"),
        (None, "none"),
    ],
)
def test_backslashcase(value, expected):
    assert module.backslashcase(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("hello", "Hello"),
        ("HelloWorld", "Hello world"),
        ("hello-world", "Hello world"),
        ("hello.world", "Hello world"),
        ("hello_world", "Hello world"),
        ("hello world", "Hello world"),
        ("", ""),
        ("ABC", "A b c"),
        ("one--two", "One  two"),
        ("  hello  ", "Hello"),
        ("hello123World", "Hello123 world"),
        (123, "123"),
        (None, "None"),
    ],
)
def test_sentencecase(value, expected):
    assert module.sentencecase(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("hello", "hello"),
        ("HelloWorld", "hello_world"),
        ("hello-world", "hello_world"),
        ("hello.world", "hello_world"),
        ("hello world", "hello_world"),
        ("", ""),
        ("ABC", "a_b_c"),
        ("already_snake", "already_snake"),
        ("one--two", "one__two"),
        ("one..two", "one__two"),
        ("one  two", "one__two"),
        ("123ABC", "123_a_b_c"),
        (123, "123"),
        (None, "none"),
    ],
)
def test_snakecase(value, expected):
    assert module.snakecase(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("hello", "hello"),
        ("HelloWorld", "hello-world"),
        ("hello-world", "hello-world"),
        ("hello.world", "hello-world"),
        ("hello world", "hello-world"),
        ("", ""),
        ("ABC", "a-b-c"),
        ("already_snake", "already-snake"),
        ("one--two", "one--two"),
        (123, "123"),
        (None, "none"),
    ],
)
def test_spinalcase(value, expected):
    assert module.spinalcase(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("hello", "hello"),
        ("HelloWorld", "hello.world"),
        ("hello-world", "hello.world"),
        ("hello.world", "hello.world"),
        ("hello world", "hello.world"),
        ("", ""),
        ("ABC", "a.b.c"),
        ("already_snake", "already.snake"),
        ("one--two", "one..two"),
        (123, "123"),
        (None, "none"),
    ],
)
def test_dotcase(value, expected):
    assert module.dotcase(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("hello", "Hello"),
        ("HelloWorld", "Hello World"),
        ("hello-world", "Hello World"),
        ("hello.world", "Hello World"),
        ("hello world", "Hello World"),
        ("", ""),
        ("ABC", "A B C"),
        ("already_snake", "Already Snake"),
        ("one--two", "One  Two"),
        ("123abc", "123abc"),
        (123, "123"),
        (None, "None"),
    ],
)
def test_titlecase(value, expected):
    assert module.titlecase(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("hello", "hello"),
        ("  hello  ", "hello"),
        ("\nhello\t", "hello"),
        ("", ""),
        ("   ", ""),
        (123, "123"),
        (None, "None"),
        (["hello"], "['hello']"),
    ],
)
def test_trimcase(value, expected):
    assert module.trimcase(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("hello", "HELLO"),
        ("Hello", "HELLO"),
        ("", ""),
        ("abc123", "ABC123"),
        (123, "123"),
        (None, "NONE"),
        (True, "TRUE"),
        ("äöü", "ÄÖÜ"),
    ],
)
def test_uppercase(value, expected):
    assert module.uppercase(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("hello", "hello"),
        ("Hello World", "HelloWorld"),
        ("hello-world", "helloworld"),
        ("hello_world", "helloworld"),
        ("hello.world", "helloworld"),
        ("hello123world", "hello123world"),
        ("", ""),
        ("!@#$%^&*()", ""),
        ("a1_b2-c3.d4", "a1b2c3d4"),
        ("  hello  ", "hello"),
        ("ABC_123", "ABC123"),
        ("café", "café"),
        (123, "123"),
    ],
)
def test_alphanumcase(value, expected):
    assert module.alphanumcase(value) == expected


@pytest.mark.parametrize(
    "function",
    [
        module.camelcase,
        module.capitalcase,
        module.constcase,
        module.lowercase,
        module.pascalcase,
        module.pathcase,
        module.backslashcase,
        module.sentencecase,
        module.snakecase,
        module.spinalcase,
        module.dotcase,
        module.titlecase,
        module.trimcase,
        module.uppercase,
    ],
)
def test_string_conversion_functions_accept_objects(function):
    class CustomObject:
        def __str__(self):
            return "HelloWorld"

    assert isinstance(function(CustomObject()), str)


@pytest.mark.parametrize(
    "function",
    [
        module.camelcase,
        module.capitalcase,
        module.constcase,
        module.lowercase,
        module.pascalcase,
        module.pathcase,
        module.backslashcase,
        module.sentencecase,
        module.snakecase,
        module.spinalcase,
        module.dotcase,
        module.titlecase,
        module.trimcase,
        module.uppercase,
    ],
)
def test_string_conversion_functions_handle_none(function):
    assert isinstance(function(None), str)


def test_alphanumcase_rejects_non_string_input():
    with pytest.raises(TypeError):
        module.alphanumcase(None)


def test_alphanumcase_rejects_integer_input():
    with pytest.raises(TypeError):
        module.alphanumcase(123)


def test_alphanumcase_rejects_list_input():
    with pytest.raises(TypeError):
        module.alphanumcase(["hello"])


def test_camelcase_converts_input_to_string():
    assert module.camelcase(123) == "123"


def test_camelcase_empty_after_string_conversion():
    assert module.camelcase("") == ""


def test_capitalcase_empty_string():
    assert module.capitalcase("") == ""


def test_sentencecase_empty_string():
    assert module.sentencecase("") == ""


def test_snakecase_empty_string():
    assert module.snakecase("") == ""


def test_pathcase_empty_string():
    assert module.pathcase("") == ""


def test_titlecase_empty_string():
    assert module.titlecase("") == ""


def test_backslashcase_empty_string():
    assert module.backslashcase("") == ""


def test_constcase_empty_string():
    assert module.constcase("") == ""


def test_pascalcase_empty_string():
    assert module.pascalcase("") == ""


def test_spinalcase_empty_string():
    assert module.spinalcase("") == ""


def test_dotcase_empty_string():
    assert module.dotcase("") == ""


def test_lowercase_empty_string():
    assert module.lowercase("") == ""


def test_uppercase_empty_string():
    assert module.uppercase("") == ""


def test_trimcase_empty_string():
    assert module.trimcase("") == ""


def test_alphanumcase_empty_string():
    assert module.alphanumcase("") == ""


def test_snakecase_preserves_existing_underscores():
    assert module.snakecase("hello_world") == "hello_world"


def test_snakecase_converts_consecutive_capitals():
    assert module.snakecase("XMLParser") == "x_m_l_parser"


def test_snakecase_converts_leading_capital():
    assert module.snakecase("Hello") == "hello"


def test_snakecase_converts_trailing_capital():
    assert module.snakecase("helloA") == "hello_a"


def test_snakecase_handles_unicode():
    assert module.snakecase("ÄBC") == "ä_b_c"


def test_sentencecase_handles_multiple_capitals():
    assert module.sentencecase("XMLParser") == "X m l parser"


def test_sentencecase_handles_leading_and_trailing_punctuation():
    assert module.sentencecase("...hello...") == "Hello"


def test_titlecase_handles_multiple_underscores():
    assert module.titlecase("hello__world") == "Hello  World"


def test_pathcase_handles_multiple_underscores():
    assert module.pathcase("hello__world") == "hello//world"


def test_backslashcase_handles_multiple_underscores():
    assert module.backslashcase("hello__world") == "hello\\\\world"


def test_alphanumcase_removes_newlines_and_tabs():
    assert module.alphanumcase("hello\nworld\t123") == "helloworld123"


def test_alphanumcase_preserves_unicode_letters():
    assert module.alphanumcase("café_日本語") == "café日本語"
