import pytest
from inflection import (
    _irregular,
    camelize,
    dasherize,
    humanize,
    ordinal,
    ordinalize,
    parameterize,
    pluralize,
    singularize,
    tableize,
    titleize,
    transliterate,
    underscore,
)

def test_camelize():
    assert camelize("device_type") == "DeviceType"
    assert camelize("device_type", False) == "deviceType"
    assert camelize("io_error") == "IoError"

def test_dasherize():
    assert dasherize("puni_puni") == "puni-puni"
    assert dasherize("already-dashed") == "already-dashed"

def test_humanize():
    assert humanize("employee_salary") == "Employee salary"
    assert humanize("author_id") == "Author"
    assert humanize("user_id") == "User"

def test_ordinal():
    assert ordinal(1) == "st"
    assert ordinal(2) == "nd"
    assert ordinal(3) == "rd"
    assert ordinal(4) == "th"
    assert ordinal(11) == "th"
    assert ordinal(12) == "th"
    assert ordinal(13) == "th"
    assert ordinal(21) == "st"
    assert ordinal(1002) == "nd"
    assert ordinal(1003) == "rd"
    assert ordinal(-11) == "th"
    assert ordinal(-1021) == "st"

def test_ordinalize():
    assert ordinalize(1) == "1st"
    assert ordinalize(2) == "2nd"
    assert ordinalize(1002) == "1002nd"
    assert ordinalize(1003) == "1003rd"
    assert ordinalize(-11) == "-11th"
    assert ordinalize(-1021) == "-1021st"

def test_parameterize():
    assert parameterize("Donald E. Knuth") == "donald-e-knuth"
    assert parameterize("Hello World!", separator="_") == "hello_world"
    assert parameterize("foo---bar") == "foo-bar"
    assert parameterize("-leading-trailing-") == "leading-trailing"
    assert parameterize("NoSeparator", separator="") == "noseparator"

def test_pluralize():
    assert pluralize("posts") == "posts"
    assert pluralize("octopus") == "octopi"
    assert pluralize("sheep") == "sheep"
    assert pluralize("CamelOctopus") == "CamelOctopi"
    assert pluralize("") == ""
    assert pluralize("equipment") == "equipment"
    assert pluralize("quiz") == "quizzes"
    assert pluralize("ox") == "oxen"
    assert pluralize("matrix") == "matrices"
    assert pluralize("tomato") == "tomatoes"
    assert pluralize("bus") == "buses"
    assert pluralize("alias") == "aliases"
    assert pluralize("axis") == "axes"
    assert pluralize("wolf") == "wolves"
    assert pluralize("life") == "lives"
    assert pluralize("analysis") == "analyses"
    assert pluralize("category") == "categories"
    assert pluralize("person") == "people"
    assert pluralize("man") == "men"
    assert pluralize("unknownword") == "unknownwords"

def test_singularize():
    assert singularize("posts") == "post"
    assert singularize("octopi") == "octopus"
    assert singularize("sheep") == "sheep"
    assert singularize("word") == "word"
    assert singularize("CamelOctopi") == "CamelOctopus"
    assert singularize("equipment") == "equipment"
    assert singularize("quizzes") == "quiz"
    assert singularize("matrices") == "matrix"
    assert singularize("vertices") == "vertex"
    assert singularize("passersby") == "passerby"
    assert singularize("oxen") == "ox"
    assert singularize("aliases") == "alias"
    assert singularize("octopuses") == "octopus"
    assert singularize("axes") == "axis"
    assert singularize("crises") == "crisis"
    assert singularize("shoes") == "shoe"
    assert singularize("oes") == "o"
    assert singularize("buses") == "bus"
    assert singularize("mice") == "mouse"
    assert singularize("boxes") == "box"
    assert singularize("movies") == "movie"
    assert singularize("series") == "series"
    assert singularize("queries") == "query"
    assert singularize("wolves") == "wolf"
    assert singularize("natives") == "native"
    assert singularize("hives") == "hive"
    assert singularize("knives") == "knife"
    assert singularize("theses") == "thesis"
    assert singularize("synopsess") == "synopsess"
    assert singularize("news") == "news"
    assert singularize("grass") == "gras"
    assert singularize("dogs") == "dog"
    assert singularize("people") == "person"
    assert singularize("men") == "man"

def test_tableize():
    assert tableize("RawScaledScorer") == "raw_scaled_scorers"
    assert tableize("egg_and_ham") == "egg_and_hams"
    assert tableize("fancyCategory") == "fancy_categories"

def test_titleize():
    assert titleize("man from the boondocks") == "Man From The Boondocks"
    assert titleize("x-men: the last stand") == "X Men: The Last Stand"
    assert titleize("TheManWithoutAPast") == "The Man Without A Past"
    assert titleize("raiders_of_the_lost_ark") == "Raiders Of The Lost Ark"

def test_transliterate():
    assert transliterate("älämölö") == "alamolo"
    assert transliterate("Ærøskøbing") == "rskbing"
    assert transliterate("normal") == "normal"

def test_underscore():
    assert underscore("DeviceType") == "device_type"
    assert underscore("IOError") == "io_error"
    assert underscore("already_underscored") == "already_underscored"
    assert underscore("dashed-string") == "dashed_string"

def test_irregular_different_starting_letter():
    _irregular("child", "children")
    assert pluralize("child") == "children"
    assert singularize("children") == "child"