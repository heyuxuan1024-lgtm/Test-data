import pytest

import stringcase


ALL_NAMES = [
    "alphanumcase",
    "backslashcase",
    "camelcase",
    "capitalcase",
    "constcase",
    "dotcase",
    "lowercase",
    "pascalcase",
    "pathcase",
    "sentencecase",
    "snakecase",
    "spinalcase",
    "titlecase",
    "trimcase",
    "uppercase",
]

STR_NAMES = [n for n in ALL_NAMES if n != "alphanumcase"]


@pytest.mark.parametrize("name", ALL_NAMES)
def test_function_exists_and_callable(name):
    assert callable(getattr(stringcase, name))


@pytest.mark.parametrize("name", STR_NAMES)
def test_empty_string_returns_empty_string(name):
    assert getattr(stringcase, name)("") == ""


@pytest.mark.parametrize("name", STR_NAMES)
def test_results_are_strings(name):
    func = getattr(stringcase, name)
    assert isinstance(func("fooBar"), str)
    assert isinstance(func(123), str)
    assert isinstance(func(None), str)


@pytest.mark.parametrize(
    "value, expected",
    [
        ("foo_bar", "fooBar"),
        ("foo_bar_baz", "fooBarBaz"),
        ("fooBar", "fooBar"),
        ("foo", "foo"),
        ("Foo", "foo"),
        ("a", "a"),
        ("A", "a"),
        ("Foo_Bar", "foo_Bar"),
        ("foo__bar", "foo_Bar"),
        ("", ""),
        ("-", "-"),
        (" ", " "),
        ("_foo", "_foo"),
        (123, "123"),
        (None, "none"),
    ],
)
def test_camelcase(value, expected):
    assert stringcase.camelcase(value) == expected


@pytest.mark.parametrize("value", ["foo-bar", "foo bar", "foo.bar"])
def test_camelcase_removes_word_nonword_word_sequences(value):
    assert stringcase.camelcase(value) == "foar"


@pytest.mark.parametrize(
    "value, expected",
    [
        ("foo", "Foo"),
        ("fOO", "FOO"),
        ("Foo", "Foo"),
        ("a", "A"),
        ("foo bar", "Foo bar"),
        ("1foo", "1foo"),
        ("", ""),
        (123, "123"),
        (None, "None"),
    ],
)
def test_capitalcase(value, expected):
    assert stringcase.capitalcase(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        ("fooBar", "FOO_BAR"),
        ("foo-bar", "FOO_BAR"),
        ("foo bar", "FOO_BAR"),
        ("foo.bar", "FOO_BAR"),
        ("foo_bar", "FOO_BAR"),
        ("FooBar", "FOO_BAR"),
        ("fooBar-baz", "FOO_BAR_BAZ"),
        ("foo", "FOO"),
        ("", ""),
        (123, "123"),
        (None, "NONE"),
    ],
)
def test_constcase(value, expected):
    assert stringcase.constcase(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        ("FOO", "foo"),
        ("Foo Bar", "foo bar"),
        ("foo", "foo"),
        ("", ""),
        (123, "123"),
        (None, "none"),
        ("\u00c0B", "\u00e0b"),
    ],
)
def test_lowercase(value, expected):
    assert stringcase.lowercase(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        ("foo", "FOO"),
        ("Foo Bar", "FOO BAR"),
        ("FOO", "FOO"),
        ("", ""),
        (123, "123"),
        (None, "NONE"),
        ("\u00e0b", "\u00c0B"),
    ],
)
def test_uppercase(value, expected):
    assert stringcase.uppercase(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        ("foo_bar", "FooBar"),
        ("foo_bar_baz", "FooBarBaz"),
        ("foo", "Foo"),
        ("fooBar", "FooBar"),
        ("foo-bar", "Foar"),
        ("", ""),
        (123, "123"),
    ],
)
def test_pascalcase(value, expected):
    assert stringcase.pascalcase(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        ("fooBar", "foo/bar"),
        ("foo-bar", "foo/bar"),
        ("foo bar", "foo/bar"),
        ("foo.bar", "foo/bar"),
        ("foo_bar", "foo/bar"),
        ("FooBarBaz", "foo/bar/baz"),
        ("foo", "foo"),
        ("", ""),
        (None, "none"),
    ],
)
def test_pathcase(value, expected):
    assert stringcase.pathcase(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        ("fooBar", "foo\\bar"),
        ("foo-bar", "foo\\bar"),
        ("foo bar", "foo\\bar"),
        ("foo_bar", "foo\\bar"),
        ("FooBarBaz", "foo\\bar\\baz"),
        ("foo", "foo"),
        ("", ""),
    ],
)
def test_backslashcase(value, expected):
    assert stringcase.backslashcase(value) == expected


def test_backslashcase_uses_single_backslash():
    result = stringcase.backslashcase("foo_bar")
    assert result.count("\\") == 1
    assert len(result) == 7


@pytest.mark.parametrize(
    "value, expected",
    [
        ("foo_bar", "Foo bar"),
        ("fooBar", "Foo bar"),
        ("FooBar", "Foo bar"),
        ("foo-bar", "Foo bar"),
        ("foo bar", "Foo bar"),
        ("foo.bar", "Foo bar"),
        ("foo", "Foo"),
        ("FOO", "F o o"),
        ("foo__bar", "Foo  bar"),
        ("   ", ""),
        ("", ""),
        (123, "123"),
    ],
)
def test_sentencecase(value, expected):
    assert stringcase.sentencecase(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        ("fooBar", "foo_bar"),
        ("FooBar", "foo_bar"),
        ("fooBarBaz", "foo_bar_baz"),
        ("foo-bar", "foo_bar"),
        ("foo bar", "foo_bar"),
        ("foo.bar", "foo_bar"),
        ("foo_bar", "foo_bar"),
        ("foo--bar", "foo__bar"),
        ("Foo", "foo"),
        ("FOO", "f_o_o"),
        ("foo", "foo"),
        ("", ""),
        (123, "123"),
        (None, "none"),
    ],
)
def test_snakecase(value, expected):
    assert stringcase.snakecase(value) == expected


def test_snakecase_is_idempotent():
    once = stringcase.snakecase("fooBar-baz")
    assert stringcase.snakecase(once) == once


@pytest.mark.parametrize(
    "value, expected",
    [
        ("fooBar", "foo-bar"),
        ("foo bar", "foo-bar"),
        ("foo_bar", "foo-bar"),
        ("foo.bar", "foo-bar"),
        ("FooBar", "foo-bar"),
        ("foo", "foo"),
        ("", ""),
    ],
)
def test_spinalcase(value, expected):
    assert stringcase.spinalcase(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        ("fooBar", "foo.bar"),
        ("foo-bar", "foo.bar"),
        ("foo bar", "foo.bar"),
        ("foo_bar", "foo.bar"),
        ("FooBar", "foo.bar"),
        ("foo", "foo"),
        ("", ""),
    ],
)
def test_dotcase(value, expected):
    assert stringcase.dotcase(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        ("foo_bar", "Foo Bar"),
        ("fooBar", "Foo Bar"),
        ("foo-bar", "Foo Bar"),
        ("foo bar", "Foo Bar"),
        ("foo.bar", "Foo Bar"),
        ("foo", "Foo"),
        ("foo__bar", "Foo  Bar"),
        ("", ""),
        (123, "123"),
    ],
)
def test_titlecase(value, expected):
    assert stringcase.titlecase(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        ("  foo ", "foo"),
        ("foo", "foo"),
        ("\t\nfoo\n", "foo"),
        ("  foo bar  ", "foo bar"),
        ("   ", ""),
        ("", ""),
        (123, "123"),
        (None, "None"),
    ],
)
def test_trimcase(value, expected):
    assert stringcase.trimcase(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        ("foo-bar_baz 1!", "foobar_baz1"),
        ("foo bar", "foobar"),
        ("abc123", "abc123"),
        ("!!!", ""),
        ("   ", ""),
        ("", ""),
        ("a.b,c;d", "abcd"),
        ("\tfoo\n", "foo"),
        ("\u00e1b!", "\u00e1b"),
    ],
)
def test_alphanumcase(value, expected):
    assert stringcase.alphanumcase(value) == expected


@pytest.mark.parametrize("value", [None, 123, 1.5, ["a"], b"abc"])
def test_alphanumcase_non_string_raises_type_error(value):
    with pytest.raises(TypeError):
        stringcase.alphanumcase(value)


def test_non_string_inputs_are_stringified():
    assert stringcase.capitalcase(12) == "12"
    assert stringcase.snakecase(12) == "12"
    assert stringcase.trimcase(1.5) == "1.5"
    assert stringcase.uppercase(True) == "TRUE"
    assert stringcase.lowercase(False) == "false"


def test_composed_conversions():
    assert stringcase.pascalcase(stringcase.snakecase("fooBarBaz")) == "FooBarBaz"
    assert stringcase.camelcase(stringcase.snakecase("fooBarBaz")) == "fooBarBaz"
    assert stringcase.spinalcase(stringcase.camelcase("foo_bar")) == "foo-bar"
    assert stringcase.titlecase(stringcase.spinalcase("fooBar")) == "Foo Bar"