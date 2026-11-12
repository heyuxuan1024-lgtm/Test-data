import pytest

import inflection


@pytest.fixture
def restore_rules():
    plurals = list(inflection.PLURALS)
    singulars = list(inflection.SINGULARS)
    uncountables = set(inflection.UNCOUNTABLES)
    yield
    inflection.PLURALS[:] = plurals
    inflection.SINGULARS[:] = singulars
    inflection.UNCOUNTABLES.clear()
    inflection.UNCOUNTABLES.update(uncountables)


def test_version():
    assert inflection.__version__ == '0.5.1'


def test_uncountables_contents():
    assert inflection.UNCOUNTABLES == {
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


def test_rule_tables_are_nonempty_lists_of_string_pairs():
    assert isinstance(inflection.PLURALS, list) and inflection.PLURALS
    assert isinstance(inflection.SINGULARS, list) and inflection.SINGULARS
    for rule, replacement in inflection.PLURALS + inflection.SINGULARS:
        assert isinstance(rule, str)
        assert isinstance(replacement, str)


@pytest.mark.parametrize(
    'word, expected',
    [
        ('quiz', 'quizzes'),
        ('Quiz', 'Quizzes'),
        ('ox', 'oxen'),
        ('oxen', 'oxen'),
        ('mouse', 'mice'),
        ('louse', 'lice'),
        ('mice', 'mice'),
        ('passerby', 'passersby'),
        ('matrix', 'matrices'),
        ('vertex', 'vertices'),
        ('index', 'indices'),
        ('box', 'boxes'),
        ('church', 'churches'),
        ('class', 'classes'),
        ('dish', 'dishes'),
        ('boss', 'bosses'),
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
        ('posts', 'posts'),
        ('person', 'people'),
        ('Person', 'People'),
        ('man', 'men'),
        ('Man', 'Men'),
        ('woman', 'women'),
        ('human', 'humans'),
        ('child', 'children'),
        ('children', 'children'),
        ('sex', 'sexes'),
        ('move', 'moves'),
        ('cow', 'kine'),
        ('Cow', 'Kine'),
        ('zombie', 'zombies'),
        ('CamelOctopus', 'CamelOctopi'),
        ('sheep', 'sheep'),
        ('fish', 'fish'),
        ('information', 'information'),
        ('Sheep', 'Sheep'),
        ('SHEEP', 'SHEEP'),
        ('Money', 'Money'),
        ('', ''),
    ],
)
def test_pluralize(word, expected):
    assert inflection.pluralize(word) == expected


@pytest.mark.parametrize(
    'word, expected',
    [
        ('posts', 'post'),
        ('octopi', 'octopus'),
        ('CamelOctopi', 'CamelOctopus'),
        ('word', 'word'),
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
        ('movies', 'movie'),
        ('news', 'news'),
        ('glass', 'glass'),
        ('testes', 'testis'),
        ('axes', 'axis'),
        ('viri', 'virus'),
        ('potatoes', 'potato'),
        ('heroes', 'hero'),
        ('cats', 'cat'),
        ('people', 'person'),
        ('People', 'Person'),
        ('CamelPeople', 'CamelPerson'),
        ('men', 'man'),
        ('women', 'woman'),
        ('humans', 'human'),
        ('children', 'child'),
        ('sexes', 'sex'),
        ('moves', 'move'),
        ('kine', 'cow'),
        ('zombies', 'zombie'),
        ('series', 'series'),
        ('sheep', 'sheep'),
        ('', ''),
    ],
)
def test_singularize(word, expected):
    assert inflection.singularize(word) == expected


@pytest.mark.parametrize(
    'word',
    [
        'equipment',
        'fish',
        'information',
        'jeans',
        'money',
        'rice',
        'series',
        'sheep',
        'species',
    ],
)
def test_uncountables_are_unchanged(word):
    assert inflection.pluralize(word) == word
    assert inflection.singularize(word) == word


def test_singularize_uncountable_at_word_boundary():
    assert inflection.singularize('big sheep') == 'big sheep'
    assert inflection.singularize('blue jeans') == 'blue jeans'


def test_singularize_uncountable_without_word_boundary_is_not_protected():
    assert inflection.singularize('bluejeans') == 'bluejean'


def test_pluralize_no_rule_match_returns_word_unchanged(restore_rules):
    inflection.PLURALS[:] = []
    assert inflection.pluralize('dog') == 'dog'


def test_singularize_no_rule_match_returns_word_unchanged(restore_rules):
    inflection.SINGULARS[:] = []
    assert inflection.singularize('dogs') == 'dogs'


def test_pluralize_applies_first_matching_rule_only(restore_rules):
    inflection.PLURALS[:] = [(r'(?i)a$', 'X'), (r'(?i)a$', 'Y')]
    assert inflection.pluralize('cata') == 'catX'


def test_singularize_applies_first_matching_rule_only(restore_rules):
    inflection.SINGULARS[:] = [(r's$', 'X'), (r's$', 'Y')]
    assert inflection.singularize('cats') == 'catX'


def test_pluralize_respects_extended_uncountables(restore_rules):
    inflection.UNCOUNTABLES.add('gizmo')
    assert inflection.pluralize('gizmo') == 'gizmo'
    assert inflection.singularize('gizmo') == 'gizmo'


def test_pluralize_none_raises():
    with pytest.raises(AttributeError):
        inflection.pluralize(123)


def test_singularize_none_raises():
    with pytest.raises(TypeError):
        inflection.singularize(None)


def test_irregular_same_first_letter_registers_rules(restore_rules):
    plural_count = len(inflection.PLURALS)
    singular_count = len(inflection.SINGULARS)
    inflection._irregular('goose', 'geese')
    assert len(inflection.PLURALS) == plural_count + 2
    assert len(inflection.SINGULARS) == singular_count + 1
    assert inflection.pluralize('goose') == 'geese'
    assert inflection.pluralize('Goose') == 'Geese'
    assert inflection.singularize('geese') == 'goose'
    assert inflection.singularize('Geese') == 'Goose'


def test_irregular_different_first_letter_registers_rules(restore_rules):
    plural_count = len(inflection.PLURALS)
    singular_count = len(inflection.SINGULARS)
    inflection._irregular('ax', 'oxen')
    assert len(inflection.PLURALS) == plural_count + 4
    assert len(inflection.SINGULARS) == singular_count + 2
    assert inflection.pluralize('ax') == 'oxen'
    assert inflection.pluralize('Ax') == 'Oxen'
    assert inflection.singularize('oxen') == 'ax'
    assert inflection.singularize('Oxen') == 'Ax'


def test_irregular_single_character_singular(restore_rules):
    inflection._irregular('a', 'as')
    assert inflection.pluralize('a') == 'as'


def test_irregular_empty_strings_raise(restore_rules):
    with pytest.raises(IndexError):
        inflection._irregular('', 'x')
    with pytest.raises(IndexError):
        inflection._irregular('x', '')


def test_camelize_uppercase_first_default():
    assert inflection.camelize('device_type') == 'DeviceType'
    assert inflection.camelize('device_type_name') == 'DeviceTypeName'
    assert inflection.camelize('device') == 'Device'
    assert inflection.camelize('') == ''


def test_camelize_lowercase_first():
    assert inflection.camelize('device_type', False) == 'deviceType'
    assert inflection.camelize('device', uppercase_first_letter=False) == 'device'
    assert inflection.camelize('Device_Type', False) == 'deviceType'


def test_camelize_underscore_edge_cases():
    assert inflection.camelize('device_') == 'Device_'
    assert inflection.camelize('device__type') == 'Device_type'
    assert inflection.camelize('_device') == '_device'


def test_camelize_inverse_of_underscore_with_caveat():
    assert inflection.camelize(inflection.underscore('IOError')) == 'IoError'


def test_camelize_lowercase_first_empty_string_raises():
    with pytest.raises(IndexError):
        inflection.camelize('', False)


def test_camelize_non_string_raises():
    with pytest.raises(TypeError):
        inflection.camelize(None)


def test_dasherize():
    assert inflection.dasherize('puni_puni') == 'puni-puni'
    assert inflection.dasherize('puni-puni') == 'puni-puni'
    assert inflection.dasherize('') == ''
    assert inflection.dasherize('__') == '--'


def test_dasherize_non_string_raises():
    with pytest.raises(AttributeError):
        inflection.dasherize(None)


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
    assert inflection.humanize(word) == expected


def test_humanize_non_string_raises():
    with pytest.raises(TypeError):
        inflection.humanize(None)


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
        (-2, 'nd'),
        ('3', 'rd'),
        (3.9, 'rd'),
    ],
)
def test_ordinal(number, expected):
    assert inflection.ordinal(number) == expected


def test_ordinal_non_numeric_string_raises():
    with pytest.raises(ValueError):
        inflection.ordinal('abc')


def test_ordinal_none_raises():
    with pytest.raises(TypeError):
        inflection.ordinal(None)


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
    assert inflection.ordinalize(number) == expected


def test_ordinalize_string_input():
    assert inflection.ordinalize('3') == '3rd'


def test_ordinalize_invalid_raises():
    with pytest.raises(ValueError):
        inflection.ordinalize('abc')
    with pytest.raises(TypeError):
        inflection.ordinalize(None)


def test_parameterize_docstring_example():
    assert inflection.parameterize('Donald E. Knuth') == 'donald-e-knuth'


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
        ('\u00c6r\u00f8sk\u00f8bing', 'rskbing'),
        ('\u00e4l\u00e4m\u00f6l\u00f6', 'alamolo'),
        ('Already-Clean', 'already-clean'),
        ('x@y#z', 'x-y-z'),
        ('100%', '100'),
    ],
)
def test_parameterize_default_separator(string, expected):
    assert inflection.parameterize(string) == expected


@pytest.mark.parametrize(
    'string, separator, expected',
    [
        ('Hello World', '_', 'hello_world'),
        ('Hello World', '', 'helloworld'),
        ('a  b', '.', 'a.b'),
        ('a..b', '.', 'a.b'),
        ('.a.', '.', 'a'),
        ('a b', '', 'ab'),
    ],
)
def test_parameterize_custom_separator(string, separator, expected):
    assert inflection.parameterize(string, separator) == expected


def test_parameterize_non_string_raises():
    with pytest.raises(TypeError):
        inflection.parameterize(None)


def test_tableize_docstring_examples():
    assert inflection.tableize('RawScaledScorer') == 'raw_scaled_scorers'
    assert inflection.tableize('egg_and_ham') == 'egg_and_hams'
    assert inflection.tableize('fancyCategory') == 'fancy_categories'


@pytest.mark.parametrize(
    'word, expected',
    [
        ('', ''),
        ('sheep', 'sheep'),
        ('Person', 'people'),
        ('PersonAccount', 'person_accounts'),
        ('Equipment', 'equipment'),
    ],
)
def test_tableize(word, expected):
    assert inflection.tableize(word) == expected


def test_tableize_non_string_raises():
    with pytest.raises(TypeError):
        inflection.tableize(None)


@pytest.mark.parametrize(
    'word, expected',
    [
        ('man from the boondocks', 'Man From The Boondocks'),
        ('x-men: the last stand', 'X Men: The Last Stand'),
        ('TheManWithoutAPast', 'The Man Without A Past'),
        ('raiders_of_the_lost_ark', 'Raiders Of The Lost Ark'),
        ('', ''),
    ],
)
def test_titleize(word, expected):
    assert inflection.titleize(word) == expected


def test_titleize_non_string_raises():
    with pytest.raises(TypeError):
        inflection.titleize(None)


@pytest.mark.parametrize(
    'string, expected',
    [
        ('\u00e4l\u00e4m\u00f6l\u00f6', 'alamolo'),
        ('\u00c6r\u00f8sk\u00f8bing', 'rskbing'),
        ('', ''),
        ('plain', 'plain'),
        ('caf\u00e9', 'cafe'),
        ('\u65e5\u672c\u8a9e', ''),
        ('\u00df', ''),
        ('na\u00efve r\u00e9sum\u00e9', 'naive resume'),
    ],
)
def test_transliterate(string, expected):
    assert inflection.transliterate(string) == expected


def test_transliterate_non_string_raises():
    with pytest.raises(TypeError):
        inflection.transliterate(None)


@pytest.mark.parametrize(
    'word, expected',
    [
        ('DeviceType', 'device_type'),
        ('device', 'device'),
        ('', ''),
        ('IOError', 'io_error'),
        ('device-type', 'device_type'),
        ('HTTPServer', 'http_server'),
        ('Device2Type', 'device2_type'),
        ('deviceType', 'device_type'),
        ('ABC', 'abc'),
        ('a-b-c', 'a_b_c'),
    ],
)
def test_underscore(word, expected):
    assert inflection.underscore(word) == expected


def test_underscore_inverse_docstring_example():
    assert inflection.camelize(inflection.underscore('IOError')) == 'IoError'


def test_underscore_non_string_raises():
    with pytest.raises(TypeError):
        inflection.underscore(None)