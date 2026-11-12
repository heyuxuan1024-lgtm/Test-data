
import pytest
import inflection


def test_version():
    assert inflection.__version__ == "0.5.1"


@pytest.mark.parametrize(
    "word, expected",
    [
        ("device_type", "DeviceType"),
        ("DeviceType", "DeviceType"),
        ("device_type_name", "DeviceTypeName"),
        ("first_name", "FirstName"),
        ("alreadyCamelized", "AlreadyCamelized"),
        ("hello_world_test", "HelloWorldTest"),
        ("hello__world", "HelloWorld"),
        ("_hello_world", "HelloWorld"),
        ("hello_world_", "HelloWorld_"),
        ("", ""),
        ("a", "A"),
        ("123_abc", "123Abc"),
        ("foo_bar123", "FooBar123"),
    ],
)
def test_camelize(word, expected):
    assert inflection.camelize(word) == expected


@pytest.mark.parametrize(
    "word, expected",
    [
        ("device_type", "deviceType"),
        ("DeviceType", "deviceType"),
        ("first_name", "firstName"),
        ("hello_world_test", "helloWorldTest"),
        ("_hello_world", "helloWorld"),
        ("hello__world", "helloWorld"),
        ("a", "a"),
        ("", ""),
    ],
)
def test_camelize_lowercase_first(word, expected):
    if word == "":
        with pytest.raises(IndexError):
            inflection.camelize(word, False)
    else:
        assert inflection.camelize(word, False) == expected


@pytest.mark.parametrize(
    "word, expected",
    [
        ("puni_puni", "puni-puni"),
        ("hello_world", "hello-world"),
        ("already-dashed", "already-dashed"),
        ("multiple_under_scores", "multiple-under-scores"),
        ("", ""),
        ("___", "---"),
        ("a_b_c", "a-b-c"),
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
        ("hello_world_test", "Hello world test"),
        ("already humanized", "Already humanized"),
        ("HELLO_WORLD", "HELLO WORLD"),
        ("user_123", "User 123"),
        ("foo_id", "Foo"),
        ("foo_bar_id", "Foo bar"),
        ("id", "Id"),
        ("", ""),
        ("123_abc", "123 abc"),
        ("FOO_bar", "FOO bar"),
    ],
)
def test_humanize(word, expected):
    assert inflection.humanize(word) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (1, "st"),
        (2, "nd"),
        (3, "rd"),
        (4, "th"),
        (5, "th"),
        (9, "th"),
        (10, "th"),
        (11, "th"),
        (12, "th"),
        (13, "th"),
        (14, "th"),
        (20, "th"),
        (21, "st"),
        (22, "nd"),
        (23, "rd"),
        (24, "th"),
        (101, "st"),
        (102, "nd"),
        (103, "rd"),
        (111, "th"),
        (112, "th"),
        (113, "th"),
        (1002, "nd"),
        (-1, "st"),
        (-2, "nd"),
        (-3, "rd"),
        (-11, "th"),
        (-1021, "st"),
        (0, "th"),
    ],
)
def test_ordinal(value, expected):
    assert inflection.ordinal(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (1, "1st"),
        (2, "2nd"),
        (3, "3rd"),
        (4, "4th"),
        (10, "10th"),
        (11, "11th"),
        (12, "12th"),
        (13, "13th"),
        (21, "21st"),
        (1002, "1002nd"),
        (1003, "1003rd"),
        (-1, "-1st"),
        (-11, "-11th"),
        (-1021, "-1021st"),
        (0, "0th"),
    ],
)
def test_ordinalize(value, expected):
    assert inflection.ordinalize(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        ("Donald E. Knuth", "donald-e-knuth"),
        ("Hello World", "hello-world"),
        ("hello_world", "hello-world"),
        ("Hello, World!", "hello-world"),
        ("  hello   world  ", "hello-world"),
        ("foo--bar", "foo-bar"),
        ("foo__bar", "foo-bar"),
        ("foo_bar-baz", "foo-bar-baz"),
        ("", ""),
        ("---", ""),
        ("___", ""),
        ("123 ABC", "123-abc"),
        ("Café", "cafe"),
        ("älämölö", "alamolo"),
        ("Ærøskøbing", "rskbing"),
        ("你好", ""),
        ("a+b=c", "a-b-c"),
    ],
)
def test_parameterize(value, expected):
    assert inflection.parameterize(value) == expected


@pytest.mark.parametrize(
    "value, separator, expected",
    [
        ("Hello World", "_", "hello_world"),
        ("Hello World", ".", "hello.world"),
        ("Hello World", "", "helloworld"),
        ("a___b", "_", "a_b"),
        ("a---b", "-", "a-b"),
        ("a...b", ".", "a.b"),
        ("--hello--", "-", "hello"),
        ("__hello__", "_", "hello"),
        ("foo bar", "+", "foo+bar"),
        ("foo/bar", ":", "foo:bar"),
    ],
)
def test_parameterize_custom_separator(value, separator, expected):
    assert inflection.parameterize(value, separator) == expected


@pytest.mark.parametrize(
    "word, expected",
    [
        ("post", "posts"),
        ("posts", "posts"),
        ("quiz", "quizzes"),
        ("ox", "oxen"),
        ("oxen", "oxen"),
        ("mouse", "mice"),
        ("louse", "lice"),
        ("passerby", "passersby"),
        ("matrix", "matrices"),
        ("vertex", "vertices"),
        ("index", "indices"),
        ("box", "boxes"),
        ("church", "churches"),
        ("class", "classes"),
        ("dish", "dishes"),
        ("city", "cities"),
        ("baby", "babies"),
        ("key", "keys"),
        ("hive", "hives"),
        ("wolf", "wolves"),
        ("knife", "knives"),
        ("analysis", "analyses"),
        ("crisis", "crises"),
        ("criterion", "criterions"),
        ("datum", "data"),
        ("medium", "media"),
        ("potato", "potatoes"),
        ("tomato", "tomatoes"),
        ("buffalo", "buffaloes"),
        ("bus", "buses"),
        ("alias", "aliases"),
        ("status", "statuses"),
        ("octopus", "octopi"),
        ("virus", "viri"),
        ("axis", "axes"),
        ("testis", "testes"),
        ("", ""),
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


@pytest.mark.parametrize(
    "word, expected",
    [
        ("Post", "Posts"),
        ("POST", "POSTS"),
        ("Quiz", "Quizzes"),
        ("OX", "OXEN"),
        ("Mouse", "Mice"),
        ("MOUSE", "MICE"),
        ("Matrix", "Matrices"),
        ("Box", "Boxes"),
        ("City", "Cities"),
        ("Baby", "Babies"),
        ("Wolf", "Wolves"),
        ("Knife", "Knives"),
        ("Octopus", "Octopi"),
        ("CamelOctopus", "CamelOctopi"),
        ("Person", "People"),
        ("PERSON", "PEOPLE"),
        ("Man", "Men"),
        ("MAN", "MEN"),
        ("Child", "Children"),
        ("CHILD", "CHILDREN"),
        ("Human", "Humans"),
        ("Cow", "Kine"),
        ("Zombie", "Zombies"),
    ],
)
def test_pluralize_case_insensitive(word, expected):
    assert inflection.pluralize(word) == expected


@pytest.mark.parametrize(
    "word, expected",
    [
        ("post", "post"),
        ("posts", "post"),
        ("quizzes", "quiz"),
        ("oxen", "ox"),
        ("mice", "mouse"),
        ("lice", "louse"),
        ("passersby", "passerby"),
        ("matrices", "matrix"),
        ("vertices", "vertex"),
        ("indices", "index"),
        ("boxes", "box"),
        ("churches", "church"),
        ("classes", "class"),
        ("dishes", "dish"),
        ("cities", "city"),
        ("babies", "baby"),
        ("keys", "key"),
        ("hives", "hive"),
        ("wolves", "wolf"),
        ("knives", "knife"),
        ("analyses", "analysis"),
        ("crises", "crisis"),
        ("theses", "thesis"),
        ("synopses", "synopsis"),
        ("prognoses", "prognosis"),
        ("parentheses", "parenthesis"),
        ("diagnoses", "diagnosis"),
        ("bases", "basis"),
        ("data", "datum"),
        ("media", "medium"),
        ("news", "news"),
        ("shoes", "shoe"),
        ("movies", "movie"),
        ("series", "series"),
        ("buses", "bus"),
        ("aliases", "alias"),
        ("statuses", "status"),
        ("octopi", "octopus"),
        ("viri", "virus"),
        ("axes", "axis"),
        ("testes", "testis"),
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
        "The fish",
        "some equipment",
        "many species",
    ],
)
def test_singularize_uncountable(word):
    assert inflection.singularize(word) == word


@pytest.mark.parametrize(
    "word, expected",
    [
        ("Posts", "Post"),
        ("POSTS", "POST"),
        ("Quizzes", "Quiz"),
        ("OXEN", "OX"),
        ("Mice", "Mouse"),
        ("MICE", "MOUSE"),
        ("Matrices", "Matrix"),
        ("Boxes", "Box"),
        ("Cities", "City"),
        ("Wolves", "Wolf"),
        ("People", "Person"),
        ("PEOPLE", "PERSON"),
        ("Men", "Man"),
        ("MEN", "MAN"),
        ("Children", "Child"),
        ("CHILDREN", "CHILD"),
        ("Humans", "Human"),
        ("Kine", "Cow"),
        ("Zombies", "Zombie"),
    ],
)
def test_singularize_case_insensitive(word, expected):
    assert inflection.singularize(word) == expected


@pytest.mark.parametrize(
    "word, expected",
    [
        ("RawScaledScorer", "raw_scaled_scorers"),
        ("egg_and_ham", "egg_and_hams"),
        ("fancyCategory", "fancy_categories"),
        ("Person", "people"),
        ("UserProfile", "user_profiles"),
        ("BlogPost", "blog_posts"),
        ("APIResponse", "api_responses"),
        ("", ""),
    ],
)
def test_tableize(word, expected):
    assert inflection.tableize(word) == expected


@pytest.mark.parametrize(
    "word, expected",
    [
        ("man from the boondocks", "Man From The Boondocks"),
        ("x-men: the last stand", "X Men: The Last Stand"),
        ("TheManWithoutAPast", "The Man Without A Past"),
        ("raiders_of_the_lost_ark", "Raiders Of The Lost Ark"),
        ("employee_salary", "Employee Salary"),
        ("hello_world", "Hello World"),
        ("first_name", "First Name"),
        ("", ""),
        ("foo-bar", "Foo Bar"),
        ("it's a test", "It's A Test"),
        ("APIResponse", "Api Response"),
        ("camelCase", "Camel Case"),
    ],
)
def test_titleize(word, expected):
    assert inflection.titleize(word) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        ("älämölö", "alamolo"),
        ("Ærøskøbing", "rskbing"),
        ("café", "cafe"),
        ("naïve", "naive"),
        ("résumé", "resume"),
        ("São Paulo", "Sao Paulo"),
        ("über", "uber"),
        ("Łódź", "odz"),
        ("你好", ""),
        ("東京", ""),
        ("hello", "hello"),
        ("", ""),
        ("éèêë", "eeee"),
        ("A\u0308", "A"),
    ],
)
def test_transliterate(value, expected):
    assert inflection.transliterate(value) == expected


@pytest.mark.parametrize(
    "word, expected",
    [
        ("DeviceType", "device_type"),
        ("deviceType", "device_type"),
        ("RawScaledScorer", "raw_scaled_scorer"),
        ("APIResponse", "api_response"),
        ("IOError", "io_error"),
        ("HTMLParser", "html_parser"),
        ("hello-world", "hello_world"),
        ("hello_world", "hello_world"),
        ("CamelCaseWord", "camel_case_word"),
        ("ABC", "abc"),
        ("A", "a"),
        ("", ""),
        ("fooBARBaz", "foo_bar_baz"),
        ("version2Value", "version2_value"),
        ("MyHTTPServer", "my_http_server"),
        ("XMLHttpRequest", "xml_http_request"),
    ],
)
def test_underscore(word, expected):
    assert inflection.underscore(word) == expected


@pytest.mark.parametrize(
    "word",
    [
        "person",
        "people",
        "man",
        "men",
        "human",
        "humans",
        "child",
        "children",
        "sex",
        "sexes",
        "move",
        "moves",
        "cow",
        "kine",
        "zombie",
        "zombies",
    ],
)
def test_irregular_plural_singular_round_trip(word):
    plural = inflection.pluralize(word)
    assert inflection.singularize(plural) == inflection.singularize(word)


@pytest.mark.parametrize(
    "word",
    [
        "person",
        "man",
        "human",
        "child",
        "sex",
        "move",
        "cow",
        "zombie",
    ],
)
def test_irregular_pluralize_singularize(word):
    plural = inflection.pluralize(word)
    assert plural != word
    assert inflection.singularize(plural).lower() == word.lower()


@pytest.mark.parametrize(
    "word",
    [
        "cat",
        "dog",
        "book",
        "table",
        "car",
        "computer",
        "word",
    ],
)
def test_regular_pluralize_then_singularize(word):
    assert inflection.singularize(inflection.pluralize(word)) == word


def test_pluralize_unknown_word():
    assert inflection.pluralize("xyz") == "xyz"


def test_singularize_unknown_word():
    assert inflection.singularize("xyz") == "xyz"


def test_pluralize_empty_string():
    assert inflection.pluralize("") == ""


def test_pluralize_case_preservation():
    assert inflection.pluralize("POST") == "POSTS"
    assert inflection.pluralize("Post") == "Posts"
    assert inflection.pluralize("post") == "posts"


def test_singularize_case_preservation():
    assert inflection.singularize("POSTS") == "POST"
    assert inflection.singularize("Posts") == "Post"
    assert inflection.singularize("posts") == "post"


@pytest.mark.parametrize(
    "function, value",
    [
        (inflection.camelize, None),
        (inflection.dasherize, None),
        (inflection.humanize, None),
        (inflection.parameterize, None),
        (inflection.pluralize, None),
        (inflection.singularize, None),
        (inflection.tableize, None),
        (inflection.titleize, None),
        (inflection.transliterate, None),
        (inflection.underscore, None),
    ],
)
def test_string_functions_reject_none(function, value):
    with pytest.raises((TypeError, AttributeError)):
        function(value)


@pytest.mark.parametrize(
    "function",
    [
        inflection.camelize,
        inflection.dasherize,
        inflection.humanize,
        inflection.parameterize,
        inflection.pluralize,
        inflection.singularize,
        inflection.tableize,
        inflection.titleize,
        inflection.transliterate,
        inflection.underscore,
    ],
)
def test_string_functions_reject_non_string(function):
    with pytest.raises((TypeError, AttributeError)):
        function(123)


@pytest.mark.parametrize(
    "value",
    [
        "0",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "10",
        "-1",
        "1.5",
    ],
)
def test_ordinalize_string_values(value):
    result = inflection.ordinalize(value)
    assert result.startswith(value)


@pytest.mark.parametrize(
    "value",
    [
        1.5,
        -1.5,
        "1.5",
        None,
        object(),
    ],
)
def test_ordinal_invalid_values(value):
    with pytest.raises((TypeError, ValueError)):
        inflection.ordinal(value)


def test_irregular_helper_same_initial_letter():
    original_plural_count = len(inflection.PLURALS)
    original_singular_count = len(inflection.SINGULARS)
    inflection._irregular("testword", "testwords")
    assert len(inflection.PLURALS) == original_plural_count + 2
    assert len(inflection.SINGULARS) == original_singular_count + 1
    assert inflection.pluralize("testword") == "testwords"
    assert inflection.singularize("testwords") == "testword"


def test_irregular_helper_different_initial_letter():
    original_plural_count = len(inflection.PLURALS)
    original_singular_count = len(inflection.SINGULARS)
    inflection._irregular("alpha", "beta")
    assert len(inflection.PLURALS) == original_plural_count + 4
    assert len(inflection.SINGULARS) == original_singular_count + 2
    assert inflection.pluralize("alpha") == "beta"
    assert inflection.singularize("beta") == "alpha"


@pytest.mark.parametrize(
    "value, expected",
    [
        ("foo_bar", "FooBar"),
        ("foo_bar", "fooBar"),
        ("a_b_c", "ABC"),
    ],
)
def test_camelize_idempotent_examples(value, expected):
    if expected == "fooBar":
        assert inflection.camelize(value, False) == expected
    else:
        assert inflection.camelize(value) == expected


def test_parameterize_repeated_custom_separator():
    assert inflection.parameterize("one---two", separator="-") == "one-two"
    assert inflection.parameterize("one___two", separator="_") == "one_two"


def test_parameterize_empty_separator():
    assert inflection.parameterize("Hello, World!", separator="") == "hello-world"


def test_ordinal_large_numbers():
    assert inflection.ordinal(10**100 + 1) == "st"
    assert inflection.ordinal(10**100 + 2) == "nd"
    assert inflection.ordinal(10**100 + 3) == "rd"
    assert inflection.ordinal(10**100 + 11) == "th"


def test_singularize_uncountable_word_inside_sentence():
    assert inflection.singularize("many fish") == "many fish"
    assert inflection.singularize("some information") == "some information"


def test_pluralize_uncountable_case_insensitive():
    assert inflection.pluralize("FISH") == "FISH"
    assert inflection.pluralize("Sheep") == "Sheep"
    assert inflection.pluralize("INFORMATION") == "INFORMATION"
