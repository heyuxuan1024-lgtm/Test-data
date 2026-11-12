
import pytest
import re
import unicodedata

import inflection


@pytest.fixture
def original_rules():
    plurals = inflection.PLURALS.copy()
    singulars = inflection.SINGULARS.copy()
    yield
    inflection.PLURALS[:] = plurals
    inflection.SINGULARS[:] = singulars


def test_version():
    assert inflection.__version__ == "0.5.1"


def test_plural_rules_exist():
    assert len(inflection.PLURALS) > 0
    assert len(inflection.SINGULARS) > 0


def test_uncountables():
    assert {
        "equipment", "fish", "information", "jeans", "money",
        "rice", "series", "sheep", "species"
    } == inflection.UNCOUNTABLES


@pytest.mark.parametrize(
    "word, expected",
    [
        ("quiz", "quizzes"),
        ("Quiz", "Quizzes"),
        ("QUIZ", "QUIZZES"),
        ("ox", "oxen"),
        ("oxen", "oxen"),
        ("mouse", "mice"),
        ("louse", "lice"),
        ("passerby", "passersby"),
        ("passersby", "passersby"),
        ("matrix", "matrices"),
        ("vertex", "vertices"),
        ("index", "indices"),
        ("box", "boxes"),
        ("church", "churches"),
        ("class", "classes"),
        ("dish", "dishes"),
        ("city", "cities"),
        ("baby", "babies"),
        ("hive", "hives"),
        ("wolf", "wolves"),
        ("leaf", "leaves"),
        ("knife", "knives"),
        ("analysis", "analyses"),
        ("basis", "bases"),
        ("datum", "data"),
        ("medium", "media"),
        ("buffalo", "buffaloes"),
        ("potato", "potatoes"),
        ("tomato", "tomatoes"),
        ("bus", "buses"),
        ("alias", "aliases"),
        ("status", "statuses"),
        ("octopus", "octopi"),
        ("virus", "viri"),
        ("axis", "axes"),
        ("testis", "testes"),
        ("book", "books"),
        ("car", "cars"),
        ("dog", "dogs"),
        ("word", "words"),
    ],
)
def test_pluralize(word, expected):
    assert inflection.pluralize(word) == expected


@pytest.mark.parametrize(
    "word",
    [
        "equipment",
        "fish",
        "information",
        "jeans",
        "money",
        "rice",
        "series",
        "sheep",
        "species",
    ],
)
def test_pluralize_uncountable(word):
    assert inflection.pluralize(word) == word


def test_pluralize_uncountable_case_insensitive():
    assert inflection.pluralize("FISH") == "FISH"
    assert inflection.pluralize("Sheep") == "Sheep"
    assert inflection.pluralize("INFORMATION") == "INFORMATION"


def test_pluralize_empty_string():
    assert inflection.pluralize("") == ""


def test_pluralize_case_preservation():
    assert inflection.pluralize("Person") == "People"
    assert inflection.pluralize("PERSON") == "PEOPLE"
    assert inflection.pluralize("Child") == "Children"
    assert inflection.pluralize("CHILD") == "CHILDREN"


def test_pluralize_irregular_words():
    assert inflection.pluralize("person") == "people"
    assert inflection.pluralize("man") == "men"
    assert inflection.pluralize("human") == "humans"
    assert inflection.pluralize("child") == "children"
    assert inflection.pluralize("sex") == "sexes"
    assert inflection.pluralize("move") == "moves"
    assert inflection.pluralize("cow") == "kine"
    assert inflection.pluralize("zombie") == "zombies"


def test_pluralize_camel_case():
    assert inflection.pluralize("CamelOctopus") == "CamelOctopi"
    assert inflection.pluralize("CamelPerson") == "CamelPeople"


def test_pluralize_already_plural():
    assert inflection.pluralize("posts") == "posts"
    assert inflection.pluralize("boxes") == "boxes"
    assert inflection.pluralize("people") == "people"


@pytest.mark.parametrize(
    "word, expected",
    [
        ("database", "database"),
        ("databases", "database"),
        ("quiz", "quiz"),
        ("quizzes", "quiz"),
        ("matrix", "matrix"),
        ("matrices", "matrix"),
        ("vertex", "vertex"),
        ("vertices", "vertex"),
        ("index", "index"),
        ("indices", "index"),
        ("passerby", "passerby"),
        ("passersby", "passerby"),
        ("ox", "ox"),
        ("oxen", "ox"),
        ("alias", "alias"),
        ("aliases", "alias"),
        ("status", "status"),
        ("statuses", "status"),
        ("octopus", "octopus"),
        ("octopi", "octopus"),
        ("virus", "virus"),
        ("viri", "virus"),
        ("axis", "axis"),
        ("axes", "axis"),
        ("crisis", "crisis"),
        ("crises", "crisis"),
        ("testis", "testis"),
        ("testes", "testis"),
        ("shoe", "shoe"),
        ("shoes", "shoe"),
        ("potato", "potato"),
        ("potatoes", "potato"),
        ("bus", "bus"),
        ("buses", "bus"),
        ("mouse", "mouse"),
        ("mice", "mouse"),
        ("box", "box"),
        ("boxes", "box"),
        ("movie", "movie"),
        ("movies", "movie"),
        ("series", "series"),
        ("city", "city"),
        ("cities", "city"),
        ("wolf", "wolf"),
        ("wolves", "wolf"),
        ("leaf", "leaf"),
        ("leaves", "leaf"),
        ("hive", "hive"),
        ("hives", "hive"),
        ("active", "active"),
        ("actives", "active"),
        ("thesis", "thesis"),
        ("theses", "thesis"),
        ("synopsis", "synopsis"),
        ("synopses", "synopsis"),
        ("analysis", "analysis"),
        ("analyses", "analysis"),
        ("basis", "basis"),
        ("bases", "basis"),
        ("news", "news"),
        ("word", "word"),
        ("words", "word"),
    ],
)
def test_singularize(word, expected):
    assert inflection.singularize(word) == expected


@pytest.mark.parametrize(
    "word",
    [
        "equipment",
        "fish",
        "information",
        "jeans",
        "money",
        "rice",
        "series",
        "sheep",
        "species",
    ],
)
def test_singularize_uncountable(word):
    assert inflection.singularize(word) == word


def test_singularize_uncountable_case_insensitive():
    assert inflection.singularize("FISH") == "FISH"
    assert inflection.singularize("Sheep") == "Sheep"
    assert inflection.singularize("INFORMATION") == "INFORMATION"


def test_singularize_uncountable_word_inside_sentence():
    assert inflection.singularize("many fish") == "many fish"
    assert inflection.singularize("the equipment") == "the equipment"


def test_singularize_empty_string():
    assert inflection.singularize("") == ""


def test_singularize_irregular_words():
    assert inflection.singularize("people") == "person"
    assert inflection.singularize("men") == "man"
    assert inflection.singularize("humans") == "human"
    assert inflection.singularize("children") == "child"
    assert inflection.singularize("sexes") == "sex"
    assert inflection.singularize("moves") == "move"
    assert inflection.singularize("kine") == "cow"
    assert inflection.singularize("zombies") == "zombie"


def test_singularize_case_preservation():
    assert inflection.singularize("People") == "Person"
    assert inflection.singularize("PEOPLE") == "PERSON"
    assert inflection.singularize("Children") == "Child"
    assert inflection.singularize("CHILDREN") == "CHILD"


def test_singularize_camel_case():
    assert inflection.singularize("CamelOctopi") == "CamelOctopus"
    assert inflection.singularize("CamelPeople") == "CamelPerson"


def test_singularize_unknown_word():
    assert inflection.singularize("computer") == "computer"
    assert inflection.singularize("xyz") == "xyz"


@pytest.mark.parametrize(
    "word, expected",
    [
        ("device_type", "DeviceType"),
        ("first_name", "FirstName"),
        ("hello_world", "HelloWorld"),
        ("device", "Device"),
        ("", ""),
        ("alreadyCamel", "AlreadyCamel"),
        ("foo_bar_baz", "FooBarBaz"),
        ("FOO_BAR", "FOOBAR"),
        ("foo__bar", "FooBar"),
        ("foo_1_bar", "Foo1Bar"),
    ],
)
def test_camelize(word, expected):
    assert inflection.camelize(word) == expected


@pytest.mark.parametrize(
    "word, expected",
    [
        ("device_type", "deviceType"),
        ("first_name", "firstName"),
        ("hello_world", "helloWorld"),
        ("foo_bar_baz", "fooBarBaz"),
        ("foo", "foo"),
        ("", ""),
    ],
)
def test_camelize_lowercase_first(word, expected):
    assert inflection.camelize(word, False) == expected


def test_camelize_multiple_underscores():
    assert inflection.camelize("foo__bar") == "FooBar"
    assert inflection.camelize("foo___bar") == "FooBar"


def test_camelize_leading_underscore():
    assert inflection.camelize("_foo") == "Foo"


def test_camelize_trailing_underscore():
    assert inflection.camelize("foo_") == "Foo"


def test_camelize_empty_lowercase():
    with pytest.raises(IndexError):
        inflection.camelize("", False)


@pytest.mark.parametrize(
    "word, expected",
    [
        ("puni_puni", "puni-puni"),
        ("hello_world", "hello-world"),
        ("already-dashed", "already-dashed"),
        ("multiple_under_scores", "multiple-under-scores"),
        ("", ""),
        ("foo__bar", "foo--bar"),
        ("foo_bar_baz", "foo-bar-baz"),
    ],
)
def test_dasherize(word, expected):
    assert inflection.dasherize(word) == expected


@pytest.mark.parametrize(
    "word, expected",
    [
        ("employee_salary", "Employee salary"),
        ("author_id", "Author"),
        ("first_name", "First name"),
        ("hello_world", "Hello world"),
        ("user_id", "User"),
        ("some_long_name_id", "Some long name"),
        ("already humanized", "Already humanized"),
        ("", ""),
        ("foo__bar", "Foo  bar"),
        ("USER_NAME", "USER NAME"),
        ("test123_name", "Test123 name"),
    ],
)
def test_humanize(word, expected):
    assert inflection.humanize(word) == expected


def test_humanize_trailing_id_only():
    assert inflection.humanize("_id") == ""
    assert inflection.humanize("id") == "Id"
    assert inflection.humanize("user_id_extra") == "User id extra"


def test_humanize_case_insensitive_id():
    assert inflection.humanize("author_ID") == "Author"
    assert inflection.humanize("author_Id") == "Author"


@pytest.mark.parametrize(
    "number, expected",
    [
        (0, "th"),
        (1, "st"),
        (2, "nd"),
        (3, "rd"),
        (4, "th"),
        (5, "th"),
        (10, "th"),
        (11, "th"),
        (12, "th"),
        (13, "th"),
        (14, "th"),
        (20, "th"),
        (21, "st"),
        (22, "nd"),
        (23, "rd"),
        (100, "th"),
        (101, "st"),
        (102, "nd"),
        (103, "rd"),
        (111, "th"),
        (112, "th"),
        (113, "th"),
        (1002, "nd"),
        (1003, "rd"),
    ],
)
def test_ordinal(number, expected):
    assert inflection.ordinal(number) == expected


@pytest.mark.parametrize(
    "number, expected",
    [
        (-1, "st"),
        (-2, "nd"),
        (-3, "rd"),
        (-11, "th"),
        (-12, "th"),
        (-13, "th"),
        (-21, "st"),
        (-1021, "st"),
        (-1022, "nd"),
        (-1023, "rd"),
    ],
)
def test_ordinal_negative(number, expected):
    assert inflection.ordinal(number) == expected


def test_ordinal_string():
    assert inflection.ordinal("1") == "st"
    assert inflection.ordinal("12") == "th"


def test_ordinal_float():
    assert inflection.ordinal(1.9) == "st"
    assert inflection.ordinal(2.9) == "nd"


def test_ordinal_invalid_value():
    with pytest.raises((TypeError, ValueError)):
        inflection.ordinal("abc")


def test_ordinal_none():
    with pytest.raises(TypeError):
        inflection.ordinal(None)


@pytest.mark.parametrize(
    "number, expected",
    [
        (1, "1st"),
        (2, "2nd"),
        (3, "3rd"),
        (4, "4th"),
        (11, "11th"),
        (12, "12th"),
        (13, "13th"),
        (21, "21st"),
        (22, "22nd"),
        (23, "23rd"),
        (1002, "1002nd"),
        (1003, "1003rd"),
        (-1, "-1st"),
        (-11, "-11th"),
        (-1021, "-1021st"),
        (0, "0th"),
    ],
)
def test_ordinalize(number, expected):
    assert inflection.ordinalize(number) == expected


def test_ordinalize_string():
    assert inflection.ordinalize("1") == "1st"


def test_ordinalize_float():
    assert inflection.ordinalize(1.9) == "1.9st"


def test_ordinalize_invalid_value():
    with pytest.raises((TypeError, ValueError)):
        inflection.ordinalize("abc")


@pytest.mark.parametrize(
    "string, expected",
    [
        ("Donald E. Knuth", "donald-e-knuth"),
        ("Hello World", "hello-world"),
        ("hello_world", "hello-world"),
        ("Already-Dashed", "already-dashed"),
        ("Hello---World", "hello-world"),
        ("hello!!!world", "hello-world"),
        ("", ""),
        ("   ", ""),
        ("foo_bar_baz", "foo-bar-baz"),
        ("C++", "c"),
        ("a/b/c", "a-b-c"),
        ("a.b.c", "a-b-c"),
        ("foo__bar", "foo-bar"),
    ],
)
def test_parameterize(string, expected):
    assert inflection.parameterize(string) == expected


def test_parameterize_custom_separator():
    assert inflection.parameterize("Hello World", "_") == "hello_world"
    assert inflection.parameterize("Hello World", ".") == "hello.world"
    assert inflection.parameterize("Hello World", "") == "helloworld"


def test_parameterize_special_separator():
    assert inflection.parameterize("a b c", "+") == "a+b+c"
    assert inflection.parameterize("a b c", "*") == "a*b*c"


def test_parameterize_unicode():
    assert inflection.parameterize("älämölö") == "alamolo"
    assert inflection.parameterize("café") == "cafe"
    assert inflection.parameterize("naïve") == "naive"
    assert inflection.parameterize("São Paulo") == "sao-paulo"


def test_parameterize_untransliterable():
    assert inflection.parameterize("Ærøskøbing") == "rskbing"


def test_parameterize_preserves_hyphens_and_underscores():
    assert inflection.parameterize("foo_bar-baz") == "foo_bar-baz"


def test_parameterize_leading_trailing_separator():
    assert inflection.parameterize("--hello--") == "hello"


def test_parameterize_repeated_custom_separator():
    assert inflection.parameterize("a   b", "-") == "a-b"
    assert inflection.parameterize("a___b", "_") == "a_b"


def test_parameterize_invalid_type():
    with pytest.raises(TypeError):
        inflection.parameterize(None)


def test_transliterate():
    assert inflection.transliterate("älämölö") == "alamolo"
    assert inflection.transliterate("café") == "cafe"
    assert inflection.transliterate("naïve") == "naive"
    assert inflection.transliterate("São Paulo") == "Sao Paulo"
    assert inflection.transliterate("hello") == "hello"


def test_transliterate_untransliterable():
    assert inflection.transliterate("Ærøskøbing") == "rskbing"
    assert inflection.transliterate("東京") == ""
    assert inflection.transliterate("你好") == ""


def test_transliterate_combining_characters():
    assert inflection.transliterate("e\u0301") == "e"


def test_transliterate_empty_string():
    assert inflection.transliterate("") == ""


def test_transliterate_invalid_type():
    with pytest.raises(TypeError):
        inflection.transliterate(None)


@pytest.mark.parametrize(
    "word, expected",
    [
        ("DeviceType", "device_type"),
        ("deviceType", "device_type"),
        ("IOError", "io_error"),
        ("HTMLParser", "html_parser"),
        ("MyClass", "my_class"),
        ("HelloWorld", "hello_world"),
        ("XMLHttpRequest", "xml_http_request"),
        ("hello-world", "hello_world"),
        ("already_snake_case", "already_snake_case"),
        ("", ""),
        ("A", "a"),
        ("ABC", "abc"),
        ("ABCDef", "abc_def"),
        ("foo123Bar", "foo123_bar"),
        ("foo-Bar", "foo_bar"),
    ],
)
def test_underscore(word, expected):
    assert inflection.underscore(word) == expected


def test_underscore_multiple_capital_groups():
    assert inflection.underscore("JSONAPIResponse") == "jsonapi_response"
    assert inflection.underscore("SimpleXMLParser") == "simple_xml_parser"


def test_underscore_numbers():
    assert inflection.underscore("Version2Type") == "version2_type"
    assert inflection.underscore("Type123ABC") == "type123_abc"


def test_tableize():
    assert inflection.tableize("RawScaledScorer") == "raw_scaled_scorers"
    assert inflection.tableize("egg_and_ham") == "egg_and_hams"
    assert inflection.tableize("fancyCategory") == "fancy_categories"


def test_tableize_irregular():
    assert inflection.tableize("Person") == "people"
    assert inflection.tableize("Child") == "children"
    assert inflection.tableize("CamelOctopus") == "camel_octopi"


def test_tableize_uncountable():
    assert inflection.tableize("Fish") == "fish"
    assert inflection.tableize("Equipment") == "equipment"


def test_tableize_empty():
    assert inflection.tableize("") == ""


@pytest.mark.parametrize(
    "word, expected",
    [
        ("man from the boondocks", "Man From The Boondocks"),
        ("x-men: the last stand", "X Men: The Last Stand"),
        ("TheManWithoutAPast", "The Man Without A Past"),
        ("raiders_of_the_lost_ark", "Raiders Of The Lost Ark"),
        ("hello_world", "Hello World"),
        ("first_name", "First Name"),
        ("foo-bar", "Foo Bar"),
        ("", ""),
        ("user_id", "User"),
        ("XMLParser", "Xml Parser"),
    ],
)
def test_titleize(word, expected):
    assert inflection.titleize(word) == expected


def test_titleize_apostrophes():
    assert inflection.titleize("don't stop") == "Don'T Stop"
    assert inflection.titleize("it's working") == "It'S Working"


def test_titleize_unicode():
    assert inflection.titleize("café society") == "Cafe Society"


def test_titleize_multiple_spaces():
    assert inflection.titleize("hello   world") == "Hello   World"


def test_titleize_irregular_words():
    assert inflection.titleize("person_address") == "Person Address"


def test_camelize_underscore_roundtrip():
    assert inflection.camelize(inflection.underscore("DeviceType")) == "DeviceType"


def test_underscore_camelize_roundtrip():
    assert inflection.underscore(inflection.camelize("device_type")) == "device_type"


def test_pluralize_singularize_roundtrip():
    words = [
        "person",
        "man",
        "child",
        "quiz",
        "box",
        "city",
        "wolf",
        "mouse",
        "octopus",
        "analysis",
        "bus",
    ]
    for word in words:
        assert inflection.singularize(inflection.pluralize(word)) == word


def test_pluralize_rule_fallback():
    assert inflection.pluralize("xyz") == "xyzs"


def test_singularize_rule_fallback():
    assert inflection.singularize("unknownword") == "unknownword"


def test_irregular_same_first_letter(original_rules):
    inflection._irregular("testword", "testwords")
    assert inflection.pluralize("testword") == "testwords"
    assert inflection.singularize("testwords") == "testword"


def test_irregular_different_first_letter(original_rules):
    inflection._irregular("mouse", "mice")
    assert inflection.pluralize("mouse") == "mice"
    assert inflection.singularize("mice") == "mouse"


def test_irregular_caseinsensitive_helper(original_rules):
    inflection._irregular("alpha", "beta")
    assert inflection.pluralize("alpha") == "beta"
    assert inflection.pluralize("Alpha") == "Beta"
    assert inflection.pluralize("ALPHA") == "BETA"
    assert inflection.singularize("beta") == "alpha"
    assert inflection.singularize("Beta") == "Alpha"


def test_irregular_plural_case_variants(original_rules):
    inflection._irregular("foo", "bar")
    assert inflection.pluralize("foo") == "bar"
    assert inflection.pluralize("Foo") == "Bar"
    assert inflection.pluralize("FOO") == "BAR"
    assert inflection.pluralize("bar") == "bar"
    assert inflection.pluralize("Bar") == "Bar"
    assert inflection.pluralize("BAR") == "BAR"


def test_irregular_empty_singular(original_rules):
    with pytest.raises(IndexError):
        inflection._irregular("", "plural")


def test_irregular_empty_plural(original_rules):
    with pytest.raises(IndexError):
        inflection._irregular("singular", "")


def test_pluralize_non_string():
    with pytest.raises(AttributeError):
        inflection.pluralize(123)


def test_singularize_non_string():
    with pytest.raises(TypeError):
        inflection.singularize(123)


def test_camelize_non_string():
    with pytest.raises(TypeError):
        inflection.camelize(123)


def test_dasherize_non_string():
    with pytest.raises(AttributeError):
        inflection.dasherize(123)


def test_humanize_non_string():
    with pytest.raises(TypeError):
        inflection.humanize(123)


def test_underscore_non_string():
    with pytest.raises(TypeError):
        inflection.underscore(123)


def test_titleize_non_string():
    with pytest.raises(TypeError):
        inflection.titleize(123)


def test_ordinalize_none():
    with pytest.raises(TypeError):
        inflection.ordinalize(None)


def test_ordinal_large_values():
    assert inflection.ordinal(10**100) == "th"
    assert inflection.ordinal(-10**100) == "th"


def test_pluralize_unicode():
    assert inflection.pluralize("café") == "cafés"


def test_singularize_unicode():
    assert inflection.singularize("cafés") == "café"


def test_parameterize_numeric_string():
    assert inflection.parameterize("123 ABC 456") == "123-abc-456"


def test_parameterize_only_special_characters():
    assert inflection.parameterize("!@#$%^&*()") == ""


def test_parameterize_multiple_separators():
    assert inflection.parameterize("hello---___world") == "hello-world"


def test_humanize_numeric():
    assert inflection.humanize("123_test") == "123 test"


def test_titleize_numeric():
    assert inflection.titleize("123_test") == "123 Test"


def test_irregular_rules_restore(original_rules):
    original_plural_count = len(inflection.PLURALS)
    original_singular_count = len(inflection.SINGULARS)
    inflection._irregular("sample", "samples")
    assert len(inflection.PLURALS) > original_plural_count
    assert len(inflection.SINGULARS) > original_singular_count
