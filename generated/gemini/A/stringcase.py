import pytest
from string_convert import (
    camelcase,
    capitalcase,
    constcase,
    lowercase,
    pascalcase,
    pathcase,
    backslashcase,
    sentencecase,
    snakecase,
    spinalcase,
    dotcase,
    titlecase,
    trimcase,
    uppercase,
    alphanumcase,
)

def test_camelcase():
    assert camelcase("foo_bar") == "fooBar"
    assert camelcase("FooBar") == "fooBar"
    assert camelcase("") == ""

def test_capitalcase():
    assert capitalcase("foo bar") == "Foo bar"
    assert capitalcase("") == ""

def test_constcase():
    assert constcase("foo_bar") == "FOO_BAR"
    assert constcase("fooBar") == "FOO_BAR"

def test_lowercase():
    assert lowercase("FOO BAR") == "foo bar"

def test_pascalcase():
    assert pascalcase("foo_bar") == "FooBar"
    assert pascalcase("") == ""

def test_pathcase():
    assert pathcase("foo_bar") == "foo/bar"
    assert pathcase("") == ""

def test_backslashcase():
    assert backslashcase("foo_bar") == "foo\\bar"

def test_sentencecase():
    assert sentencecase("foo_bar") == "Foo bar"
    assert sentencecase("fooBar") == "Foo bar"
    assert sentencecase("") == ""

def test_snakecase():
    assert snakecase("fooBar") == "foo_bar"
    assert snakecase("foo-bar") == "foo_bar"
    assert snakecase("") == ""

def test_spinalcase():
    assert spinalcase("foo_bar") == "foo-bar"

def test_dotcase():
    assert dotcase("foo_bar") == "foo.bar"

def test_titlecase():
    assert titlecase("foo_bar") == "Foo Bar"

def test_trimcase():
    assert trimcase("  foo  ") == "foo"

def test_uppercase():
    assert uppercase("foo bar") == "FOO BAR"

def test_alphanumcase():
    assert alphanumcase("foo_bar-123!") == "foo_bar123"