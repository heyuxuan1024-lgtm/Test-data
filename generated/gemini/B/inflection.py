import pytest
import inflection

def test_camelize():
    assert inflection.camelize("device_type") == "DeviceType"
    assert inflection.camelize("device_type", False) == "deviceType"
    assert inflection.camelize("io_error") == "IoError"

def test_dasherize():
    assert inflection.dasherize("puni_puni") == "puni-puni"
    assert inflection.dasherize("already-dashed") == "already-dashed"

def test_humanize():
    assert inflection.humanize("employee_salary") == "Employee salary"
    assert inflection.humanize("author_id") == "Author"
    assert inflection.humanize("user_id") == "User"

def test_ordinal():
    assert inflection.ordinal(1) == "st"
    assert inflection.ordinal(2) == "nd"
    assert inflection.ordinal(3) == "rd"
    assert inflection.ordinal(4) == "th"
    assert inflection.ordinal(11) == "th"
    assert inflection.ordinal(12) == "th"
    assert inflection.ordinal(13) == "th"
    assert inflection.ordinal(21) == "st"
    assert inflection.ordinal(1002) == "nd"
    assert inflection.ordinal(1003) == "rd"
    assert inflection.ordinal(-11) == "th"
    assert inflection.ordinal(-1021) == "st"

def test_ordinalize():
    assert inflection.ordinalize(1) == "1st"
    assert inflection.ordinalize(2) == "2nd"
    assert inflection.ordinalize(1002) == "1002nd"
    assert inflection.ordinalize(1003) == "1003rd"
    assert inflection.ordinalize(-11) == "-11th"
    assert inflection.ordinalize(-1021) == "-1021st"

def test_parameterize():
    assert inflection.parameterize("Donald E. Knuth") == "donald-e-knuth"
    assert inflection.parameterize("Hello World!", separator="_") == "hello_world"
    assert inflection.parameterize("foo---bar") == "foo-bar"
    assert inflection.parameterize("-leading-trailing-") == "leading-trailing"
    assert inflection.parameterize("NoSeparator", separator="") == "noseparator"

def test_pluralize():
    assert inflection.pluralize("posts") == "posts"
    assert inflection.pluralize("octopus") == "octopi"
    assert inflection.pluralize("sheep") == "sheep"
    assert inflection.pluralize("CamelOctopus") == "CamelOctopi"
    assert inflection.pluralize("") == ""
    assert inflection.pluralize("equipment") == "equipment"
    assert inflection.pluralize("quiz") == "quizzes"
    assert inflection.pluralize("ox") == "oxen"
    assert inflection.pluralize("matrix") == "matrices"
    assert inflection.pluralize("tomato") == "tomatoes"
    assert inflection.pluralize("bus") == "buses"
    assert inflection.pluralize("alias") == "aliases"
    assert inflection.pluralize("axis") == "axes"
    assert inflection.pluralize("wolf") == "wolves"
    assert inflection.pluralize("life") == "lives"
    assert inflection.pluralize("analysis") == "analyses"
    assert inflection.pluralize("category") == "categories"
    assert inflection.pluralize("person") == "people"
    assert inflection.pluralize("man") == "men"
    assert inflection.pluralize("unknownword") == "unknownwords"

def test_singularize():
    assert inflection.singularize("posts") == "post"
    assert inflection.singularize("octopi") == "octopus"
    assert inflection.singularize("sheep") == "sheep"
    assert inflection.singularize("word") == "word"
    assert inflection.singularize("CamelOctopi") == "CamelOctopus"
    assert inflection.singularize("equipment") == "equipment"
    assert inflection.singularize("quizzes") == "quiz"
    assert inflection.singularize("matrices") == "matrix"
    assert inflection.singularize("vertices") == "vertex"
    assert inflection.singularize("passersby") == "passerby"
    assert inflection.singularize("oxen") == "ox"
    assert inflection.singularize("aliases") == "alias"
    assert inflection.singularize("octopuses") == "octopus"
    assert inflection.singularize("axes") == "axis"
    assert inflection.singularize("crises") == "crisis"
    assert inflection.singularize("shoes") == "shoe"
    assert inflection.singularize("oes") == "o"
    assert inflection.singularize("buses") == "bus"
    assert inflection.singularize("mice") == "mouse"
    assert inflection.singularize("boxes") == "box"
    assert inflection.singularize("movies") == "movie"
    assert inflection.singularize("series") == "series"
    assert inflection.singularize("queries") == "query"
    assert inflection.singularize("wolves") == "wolf"
    assert inflection.singularize("natives") == "native"
    assert inflection.singularize("hives") == "hive"
    assert inflection.singularize("knives") == "knife"
    assert inflection.singularize("theses") == "thesis"
    assert inflection.singularize("synopsess") == "synopsess"
    assert inflection.singularize("news") == "news"
    assert inflection.singularize("grass") == "gras"
    assert inflection.singularize("dogs") == "dog"
    assert inflection.singularize("people") == "person"
    assert inflection.singularize("men") == "man"

def test_tableize():
    assert inflection.tableize("RawScaledScorer") == "raw_scaled_scorers"
    assert inflection.tableize("egg_and_ham") == "egg_and_hams"
    assert inflection.tableize("fancyCategory") == "fancy_categories"

def test_titleize():
    assert inflection.titleize("man from the boondocks") == "Man From The Boondocks"
    assert inflection.titleize("x-men: the last stand") == "X Men: The Last Stand"
    assert inflection.titleize("TheManWithoutAPast") == "The Man Without A Past"
    assert inflection.titleize("raiders_of_the_lost_ark") == "Raiders Of The Lost Ark"

def test_transliterate():
    assert inflection.transliterate("älämölö") == "alamolo"
    assert inflection.transliterate("Ærøskøbing") == "rskbing"
    assert inflection.transliterate("normal") == "normal"

def test_underscore():
    assert inflection.underscore("DeviceType") == "device_type"
    assert inflection.underscore("IOError") == "io_error"
    assert inflection.underscore("already_underscored") == "already_underscored"
    assert inflection.underscore("dashed-string") == "dashed_string"

def test_irregular_different_starting_letter():
    inflection._irregular("child", "children")
    assert inflection.pluralize("child") == "children"
    assert inflection.singularize("children") == "child"