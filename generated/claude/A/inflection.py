import pytest

import inflection
from inflection import (
    PLURALS,
    SINGULARS,
    UNCOUNTABLES,
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


@pytest.fixture
def restore_rules():
    plurals = list(PLURALS)
    singulars = list(SINGULARS)
    uncountables = set(UNCOUNTABLES)
    yield
    PLURALS[:] = plurals
    SINGULARS[:] = singulars
    UNCOUNTABLES.clear()
    UNCOUNTABLES.update(uncountables)


def test_version():
    assert inflection.__version__ == '0.5.1'


def test_uncountables_contents():
    assert UNCOUNTABLES == {
        'equipment',
        'fish',
        'information',
        'jeans',
        'money',
        'rice',
        'series',
        'sheep',
        'species',
    }


def test_rule_tables_are_nonempty_lists_of_pairs():
    assert isinstance(PLURALS, list) and PLURALS
    assert isinstance(SINGULARS, list) and SINGULARS
    for rule, replacement in PLURALS + SINGULARS:
        assert isinstance(rule, str)
        assert isinstance(replacement, str)


@pytest.mark.parametrize(
    'word, expected',
    [
        ('quiz', 'quizzes'),
        ('Quiz', 'Quizzes'),
        ('ox', 'oxen'),
        ('OX', 'OXEN'),
        ('oxen', 'oxen'),
        ('mouse', 'mice'),
        ('louse', 'lice'),
        ('dice', 'dice'),
        ('passerby', 'passersby'),
        ('matrix', 'matrices'),
        ('vertex', 'vertices'),
        ('index', 'indices'),
        ('ax', 'axes'),
        ('box', 'boxes'),
        ('church', 'churches'),
        ('class', 'classes'),
        ('dish', 'dishes'),
        ('city', 'cities'),
        ('day', 'days'),
        ('key', 'keys'),
        ('hive', 'hives'),
        ('half', 'halves'),
        ('wolf', 'wolves'),
        ('knife', 'knives'),
        ('wife', 'wives'),
        ('crisis', 'crises'),
        ('analysis', 'analyses'),
        ('criteria', 'criteria'),
        ('phenomenon', 'phenomena'),
        ('bus', 'buses'),
        ('alias', 'aliases'),
        ('status', 'statuses'),
        ('octopus', 'octopi'),
        ('virus', 'viri'),
        ('axis', 'axes'),
        ('testis', 'testes'),
        ('buffalo', 'buffaloes'),
        ('potato', 'potatoes'),
        ('tomato', 'tomatoes'),
        ('photo', 'photos'),
        ('cat', 'cats'),
        ('dog', 'dogs'),
        ('house', 'houses'),
        ('boss', 'bosses'),
        ('person', 'people'),
        ('man', 'men'),
        ('woman', 'women'),
        ('human', 'humans'),
        ('child', 'children'),
        ('sex', 'sexes'),
        ('move', 'moves'),
        ('cow', 'kine'),
        ('zombie', 'zombies'),
        ('Person', 'People'),
        ('PERSON', 'PEOPLE'),
        ('Man', 'Men'),
        ('CamelOctopus', 'CamelOctopi'),
        ('posts', 'posts'),
        ('sheep', 'sheep'),
        ('fish', 'fish'),
        ('information', 'information'),
        ('Sheep', 'Sheep'),
        ('', ''),
    ],
)
def test_pluralize(word, expected):
    assert pluralize(word) == expected


@pytest.mark.parametrize(
    'word, expected',
    [
        ('posts', 'post'),
        ('octopi', 'octopus'),
        ('sheep', 'sheep'),
        ('word', 'word'),
        ('CamelOctopi', 'CamelOctopus'),
        ('quizzes', 'quiz'),
        ('oxen', 'ox'),
        ('mice', 'mouse'),
        ('lice', 'louse'),
        ('matrices', 'matrix'),
        ('vertices', 'vertex'),
        ('indices', 'index'),
        ('passersby', 'passerby'),
        ('databases', 'database'),
        ('aliases', 'alias'),
        ('statuses', 'status'),
        ('buses', 'bus'),
        ('buses', 'bus'),
        ('shoes', 'shoe'),
        ('boxes', 'box'),
        ('churches', 'church'),
        ('classes', 'class'),
        ('dishes', 'dish'),
        ('cities', 'city'),
        ('days', 'day'),
        ('hives', 'hive'),
        ('halves', 'half'),
        ('wolves', 'wolf'),
        ('knives', 'knife'),
        ('wives', 'wife'),
        ('crises', 'crisis'),
        ('analyses', 'analysis'),
        ('phenomena', 'phenomenon'),
        ('movies', 'movie'),
        ('series', 'series'),
        ('news', 'news'),
        ('glass', 'glass'),
        ('testes', 'testis'),
        ('axes', 'axis'),
        ('viri', 'virus'),
        ('potatoes', 'potato'),
        ('heroes', 'hero'),
        ('cats', 'cat'),
        ('people', 'person'),
        ('men', 'man'),
        ('women', 'woman'),
        ('humans', 'human'),
        ('children', 'child'),
        ('sexes', 'sex'),
        ('moves', 'move'),
        ('kine', 'cow'),
        ('zombies', 'zombie'),
        ('People', 'Person'),
        ('MEN', 'MAN'),
        ('CHILDREN', 'CHILD'),
        ('CamelPeople', 'CamelPerson'),
        ('', ''),
    ],
)
def test_singularize(word, expected):
    assert singularize(word) == expected


@pytest.mark.parametrize('word', ['equipment', 'fish', 'information', 'jeans', 'money', 'rice', 'series', 'sheep', 'species'])
def test_uncountables_round_trip(word):
    assert pluralize(word) == word
    assert singularize(word) == word


def test_pluralize_and_singularize_none_or_empty():
    assert pluralize('') == ''
    assert singularize('') == ''


def test_pluralize_uncountable_case_insensitive_via_lower():
    assert pluralize('SHEEP') == 'SHEEP'
    assert pluralize('Money') == 'Money'


def test_singularize_uncountable_suffix_match():
    assert singularize('blue_sheep') == 'blue_sheep'
    assert singularize('the_fish') == 'the_fish'


def test_singularize_uncountable_requires_word_boundary():
    assert singularize('thefish') == 'thefish'


def test_singularize_uncountable_not_suffix_only_for_plural_form():
    assert singularize('ricey') == 'ricey'


def test_pluralize_no_rule_match_returns_word_unchanged(restore_rules):
    PLURALS[:] = []
    assert pluralize('dog') == 'dog'


def test_singularize_no_rule_match_returns_word_unchanged(restore_rules):
    SINGULARS[:] = []
    assert singularize('dogs') == 'dogs'


def test_pluralize_applies_first_matching_rule_only(restore_rules):
    PLURALS[:] = [(r'(?i)a$', 'X'), (r'(?i)a$', 'Y')]
    assert pluralize('cata') == 'catX'


def test_singularize_applies_first_matching_rule_only(restore_rules):
    SINGULARS[:] = [(r's$', 'X'), (r's$', 'Y')]
    assert singularize('cats') == 'catX'


def test_irregular_same_first_letter_registers_rules(restore_rules):
    _irregular('goose', 'geese')
    assert pluralize('goose') == 'geese'
    assert singularize('geese') == 'goose'
    assert pluralize('Goose') == 'Geese'


def test_irregular_different_first_letter_registers_rules(restore_rules):
    _irregular('ax', 'oxen')
    assert pluralize('ax') == 'oxen'
    assert pluralize('AX') == 'OXEN'
    assert singularize('oxen') == 'ax'
    assert singularize('OXEN') == 'AX'


def test_irregular_plural_first_letter_upper_variant(restore_rules):
    _irregular('foo', 'Bars')
    assert pluralize('foo') == 'Bars'
    assert singularize('Bars') == 'foo'


def test_irregular_single_character_words(restore_rules):
    _irregular('a', 'as')
    assert pluralize('a') == 'as'


def test_irregular_empty_strings_raise(restore_rules):
    with pytest.raises(IndexError):
        _irregular('', 'x')
    with pytest.raises(IndexError):
        _irregular('x', '')


def test_camelize_uppercase_first_default():
    assert camelize('device_type') == 'DeviceType'
    assert camelize('device') == 'Device'
    assert camelize('') == ''


def test_camelize_lowercase_first():
    assert camelize('device_type', False) == 'deviceType'
    assert camelize('device', uppercase_first_letter=False) == 'device'


def test_camelize_underscore_edge_cases():
    assert camelize('_device') == 'Device'
    assert camelize('device__type') == 'Device_Type'
    assert camelize('device_') == 'Device'
    assert camelize('_') == ''


def test_camelize_inverse_of_underscore_with_caveat():
    assert camelize(underscore('IOError')) == 'IoError'


def test_camelize_lowercase_first_empty_string_raises():
    with pytest.raises(IndexError):
        camelize('', False)


def test_dasherize():
    assert dasherize('puni_puni') == 'puni-puni'
    assert dasherize('puni-puni') == 'puni-puni'
    assert dasherize('') == ''
    assert dasherize('__') == '--'


def test_dasherize_non_string_raises():
    with pytest.raises(AttributeError):
        dasherize(None)


@pytest.mark.parametrize(
    'word, expected',
    [
        ('employee_salary', 'Employee salary'),
        ('author_id', 'Author'),
        ('author_id_id', 'Author id'),
        ('', ''),
        ('x', 'X'),
        ('_', ' '),
        ('ALL_CAPS', 'All caps'),
        ('mixed_Case_Word', 'Mixed case word'),
        ('id', 'Id'),
        ('_id', ''),
        ('123_abc', '123 abc'),
    ],
)
def test_humanize(word, expected):
    assert humanize(word) == expected


def test_humanize_non_string_raises():
    with pytest.raises(TypeError):
        humanize(None)


@pytest.mark.parametrize(
    'number, expected',
    [
        (0, 'th'),
        (1, 'st'),
        (2, 'nd'),
        (3, 'rd'),
        (4, 'th'),
        (9, 'th'),
        (10, 'th'),
        (11, 'th'),
        (12, 'th'),
        (13, 'th'),
        (14, 'th'),
        (21, 'st'),
        (22, 'nd'),
        (23, 'rd'),
        (101, 'st'),
        (111, 'th'),
        (112, 'th'),
        (113, 'th'),
        (1002, 'nd'),
        (1003, 'rd'),
        (-11, 'th'),
        (-1021, 'st'),
        ('3', 'rd'),
        (3.9, 'rd'),
        (-2, 'nd'),
    ],
)
def test_ordinal(number, expected):
    assert ordinal(number) == expected


def test_ordinal_non_numeric_string_raises():
    with pytest.raises(ValueError):
        ordinal('abc')


def test_ordinal_none_raises():
    with pytest.raises(TypeError):
        ordinal(None)


@pytest.mark.parametrize(
    'number, expected',
    [
        (1, '1st'),
        (2, '2nd'),
        (1002, '1002nd'),
        (1003, '1003rd'),
        (-11, '-11th'),
        (-1021, '-1021st'),
        (0, '0th'),
        (12, '12th'),
    ],
)
def test_ordinalize(number, expected):
    assert ordinalize(number) == expected


def test_ordinalize_string_input_uses_format():
    assert ordinalize('3') == '33rd'[0:0] + '3' + 'rd'


def test_parameterize_docstring_example():
    assert parameterize('Donald E. Knuth') == 'donald-e-knuth'


@pytest.mark.parametrize(
    'string, expected',
    [
        ('', ''),
        ('   ', ''),
        ('Hello World', 'hello-world'),
        ('hello_world', 'hello_world'),
        ('a--b', 'a-b'),
        ('a---b', 'a-b'),
        ('-a-', 'a'),
        ('--a--', 'a'),
        ('!!!', ''),
        ('Ærøskøbing', 'rskbing'),
        ('älämölö', 'alamolo'),
        ('Already-Clean', 'already-clean'),
        ('x@y#z', 'x-y-z'),
        ('100%', '100'),
    ],
)
def test_parameterize_default_separator(string, expected):
    assert parameterize(string) == expected


@pytest.mark.parametrize(
    'string, separator, expected',
    [
        ('Hello World', '_', 'hello_world'),
        ('Hello World', '', 'helloworld'),
        ('a  b', '.', 'a.b'),
        ('a..b', '.', 'a.b'),
        ('.a.', '.', 'a'),
        ('a b', '', 'ab'),
        ('a-b', '_', 'a_b'),
    ],
)
def test_parameterize_custom_separator(string, separator, expected):
    assert parameterize(string, separator) == expected


def test_parameterize_separator_none_skips_cleanup():
    assert parameterize('a b', None) == 'a b'


def test_parameterize_non_string_raises():
    with pytest.raises(TypeError):
        parameterize(None)


def test_tableize_docstring_examples():
    assert tableize('RawScaledScorer') == 'raw_scaled_scorers'