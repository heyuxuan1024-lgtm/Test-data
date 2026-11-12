
import pickle
import re
import warnings

import pytest

import your_module as version_module
from your_module import (
    InvalidVersion,
    Version,
    normalize_pre,
    parse,
)

_BaseVersion = version_module._BaseVersion
_TrimmedRelease = version_module._TrimmedRelease
_Version = version_module._Version
_cmpkey = version_module._cmpkey
_parse_letter_version = version_module._parse_letter_version
_parse_local_version = version_module._parse_local_version
_validate_epoch = version_module._validate_epoch
_validate_release = version_module._validate_release
_validate_pre = version_module._validate_pre
_validate_post = version_module._validate_post
_validate_dev = version_module._validate_dev
_validate_local = version_module._validate_local


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("alpha", "a"),
        ("ALPHA", "a"),
        ("beta", "b"),
        ("BETA", "b"),
        ("c", "rc"),
        ("C", "rc"),
        ("pre", "rc"),
        ("PRE", "rc"),
        ("preview", "rc"),
        ("PREVIEW", "rc"),
        ("rev", "post"),
        ("REV", "post"),
        ("r", "post"),
        ("R", "post"),
        ("rc", "rc"),
        ("post", "post"),
        ("dev", "dev"),
        ("unknown", "unknown"),
        ("", ""),
    ],
)
def test_normalize_pre(value, expected):
    assert normalize_pre(value) == expected


def test_normalize_pre_requires_string():
    with pytest.raises(AttributeError):
        normalize_pre(None)


def test_normalize_pre_is_positional_only():
    with pytest.raises(TypeError):
        normalize_pre(letter="alpha")


def test_parse_returns_version():
    result = parse("1.2.3")
    assert isinstance(result, Version)
    assert str(result) == "1.2.3"


def test_parse_invalid_version():
    with pytest.raises(InvalidVersion):
        parse("not-a-version")


def test_module_dir():
    assert version_module.__dir__() == version_module.__all__


@pytest.mark.parametrize(
    "value",
    [
        "0",
        "1",
        "1.0",
        "1.2.3",
        "10.20.30.40",
        "v1.2.3",
        "V1.2.3",
        " 1.2.3 ",
        "1!2.3",
        "2!0.0",
        "1.0a1",
        "1.0alpha1",
        "1.0A1",
        "1.0b2",
        "1.0beta2",
        "1.0rc3",
        "1.0c3",
        "1.0pre3",
        "1.0preview3",
        "1.0.post1",
        "1.0post1",
        "1.0rev1",
        "1.0r1",
        "1.0-1",
        "1.0.dev1",
        "1.0dev1",
        "1.0a1.post2.dev3",
        "1.0+abc",
        "1.0+ABC",
        "1.0+abc.1",
        "1.0+abc-1",
        "1.0+abc_1",
        "1.0+1.2",
        "1.0+abc.def.ghi",
        "1.0a",
        "1.0b",
        "1.0rc",
        "1.0.post",
        "1.0.dev",
    ],
)
def test_valid_version_strings(value):
    assert isinstance(Version(value), Version)


@pytest.mark.parametrize(
    "value",
    [
        "",
        " ",
        "invalid",
        "one.two",
        "1..2",
        ".1",
        "1.",
        "..",
        "1.2..3",
        "1a",
        "1+",
        "1++abc",
        "1.0+abc+def",
        "1.0+abc..def",
        "1.0+abc--def",
        "1.0+abc__def",
        "1.0+abc.",
        "1.0+abc-",
        "1.0+abc_",
        "1.0+é",
        "1.0@",
        "1.0!",
        "!1.0",
        "1!1!1.0",
        "1.0a-",
        "1.0post-",
        "1.0dev-",
        "1.0rc+",
        "v",
        "vv1.0",
        "1.0 foo",
        "1.0\n",
    ],
)
def test_invalid_version_strings(value):
    with pytest.raises(InvalidVersion):
        Version(value)


@pytest.mark.parametrize("value", [None, 1, 1.0, [], {}, object()])
def test_version_rejects_non_string_input(value):
    with pytest.raises(InvalidVersion):
        Version(value)


def test_version_invalid_input_has_no_chained_exception_for_type_error():
    with pytest.raises(InvalidVersion) as exc_info:
        Version(123)
    assert exc_info.value.__cause__ is None


def test_version_invalid_regex_input_has_no_chained_exception():
    with pytest.raises(InvalidVersion) as exc_info:
        Version(None)
    assert exc_info.value.__cause__ is None


def test_version_simple_numeric_path():
    version = Version("1.2.3")
    assert version.epoch == 0
    assert version.release == (1, 2, 3)
    assert version.pre is None
    assert version.post is None
    assert version.dev is None
    assert version.local is None


def test_version_simple_numeric_zero():
    version = Version("0")
    assert version.release == (0,)
    assert str(version) == "0"


def test_version_large_release_components():
    version = Version("1.100000.999999")
    assert version.release == (1, 100000, 999999)


def test_version_epoch_and_release():
    version = Version("2!1.2.3")
    assert version.epoch == 2
    assert version.release == (1, 2, 3)
    assert str(version) == "2!1.2.3"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("1.0a1", ("a", 1)),
        ("1.0alpha1", ("a", 1)),
        ("1.0A1", ("a", 1)),
        ("1.0b2", ("b", 2)),
        ("1.0beta2", ("b", 2)),
        ("1.0rc3", ("rc", 3)),
        ("1.0c3", ("rc", 3)),
        ("1.0pre3", ("rc", 3)),
        ("1.0preview3", ("rc", 3)),
        ("1.0a", ("a", 0)),
        ("1.0b", ("b", 0)),
        ("1.0rc", ("rc", 0)),
    ],
)
def test_prerelease_parsing(value, expected):
    assert Version(value).pre == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("1.0-1", 1),
        ("1.0.post1", 1),
        ("1.0post1", 1),
        ("1.0rev1", 1),
        ("1.0r1", 1),
        ("1.0.post", 0),
        ("1.0post", 0),
    ],
)
def test_postrelease_parsing(value, expected):
    assert Version(value).post == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("1.0.dev1", 1),
        ("1.0dev1", 1),
        ("1.0.dev", 0),
        ("1.0dev", 0),
    ],
)
def test_development_release_parsing(value, expected):
    assert Version(value).dev == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("1.0+abc", "abc"),
        ("1.0+ABC", "abc"),
        ("1.0+abc.1", "abc.1"),
        ("1.0+abc-1", "abc.1"),
        ("1.0+abc_1", "abc.1"),
        ("1.0+1.2", "1.2"),
        ("1.0+ABC.Def-GHI", "abc.def.ghi"),
    ],
)
def test_local_version_parsing(value, expected):
    assert Version(value).local == expected


def test_version_string_normalization():
    assert str(Version("v1.0")) == "1.0"
    assert str(Version("1.0-alpha1")) == "1.0a1"
    assert str(Version("1.0_beta2")) == "1.0b2"
    assert str(Version("1.0-preview3")) == "1.0rc3"
    assert str(Version("1.0-1")) == "1.0.post1"
    assert str(Version("1.0+ABC_DEF")) == "1.0+abc.def"


def test_version_repr():
    assert repr(Version("1.2.3")) == "<Version('1.2.3')>"


def test_version_str_round_trip():
    values = [
        "1",
        "1.2.3",
        "1!2.3",
        "1.0a1",
        "1.0b2",
        "1.0rc3",
        "1.0.post1",
        "1.0.dev1",
        "1.0a1.post2.dev3+abc.1",
    ]
    for value in values:
        normalized = str(Version(value))
        assert str(Version(normalized)) == normalized


def test_version_properties_for_stable_release():
    version = Version("1.2.3")
    assert version.epoch == 0
    assert version.release == (1, 2, 3)
    assert version.pre is None
    assert version.post is None
    assert version.dev is None
    assert version.local is None
    assert version.public == "1.2.3"
    assert version.base_version == "1.2.3"
    assert not version.is_prerelease
    assert not version.is_postrelease
    assert not version.is_devrelease
    assert version.major == 1
    assert version.minor == 2
    assert version.micro == 3


def test_version_properties_for_complex_release():
    version = Version("2!1.2.3a4.post5.dev6+ABC.7")
    assert version.epoch == 2
    assert version.release == (1, 2, 3)
    assert version.pre == ("a", 4)
    assert version.post == 5
    assert version.dev == 6
    assert version.local == "abc.7"
    assert version.public == "2!1.2.3a4.post5.dev6"
    assert version.base_version == "2!1.2.3"
    assert version.is_prerelease
    assert version.is_postrelease
    assert version.is_devrelease
    assert version.major == 1
    assert version.minor == 2
    assert version.micro == 3


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("1", (1, 0, 0)),
        ("1.2", (1, 2, 0)),
        ("1.2.3", (1, 2, 3)),
        ("0", (0, 0, 0)),
        ("1.2.3.4", (1, 2, 3)),
    ],
)
def test_major_minor_micro(value, expected):
    version = Version(value)
    assert (version.major, version.minor, version.micro) == expected


def test_public_excludes_local_segment():
    assert Version("1.2.3+abc").public == "1.2.3"


def test_base_version_excludes_release_suffixes():
    assert Version("1!2.3a1.post2.dev3+abc").base_version == "1!2.3"


def test_is_prerelease_for_prerelease():
    assert Version("1.0a1").is_prerelease
    assert Version("1.0b1").is_prerelease
    assert Version("1.0rc1").is_prerelease


def test_is_prerelease_for_dev_only():
    assert Version("1.0.dev1").is_prerelease


def test_is_postrelease_without_post():
    assert not Version("1.0").is_postrelease


def test_is_devrelease_without_dev():
    assert not Version("1.0").is_devrelease


@pytest.mark.parametrize(
    ("left", "right"),
    [
        ("1", "1.0"),
        ("1.0", "1.0.0"),
        ("1.0.0", "1.0.0.0"),
        ("1.0+ABC", "1.0+abc"),
        ("1.0-alpha1", "1.0a1"),
        ("1.0-preview1", "1.0rc1"),
        ("1.0-1", "1.0.post1"),
    ],
)
def test_equivalent_versions(left, right):
    assert Version(left) == Version(right)
    assert not Version(left) != Version(right)
    assert hash(Version(left)) == hash(Version(right))


def test_version_comparison_operators():
    lower = Version("1.0")
    equal = Version("1.0.0")
    higher = Version("2.0")

    assert lower < higher
    assert lower <= higher
    assert higher > lower
    assert higher >= lower
    assert lower <= equal
    assert lower >= equal
    assert lower == equal
    assert not lower != equal
    assert lower != higher


@pytest.mark.parametrize(
    ("earlier", "later"),
    [
        ("1.0.dev1", "1.0a1"),
        ("1.0a1", "1.0b1"),
        ("1.0b1", "1.0rc1"),
        ("1.0rc1", "1.0"),
        ("1.0", "1.0.post1"),
        ("1.0.dev1", "1.0.dev2"),
        ("1.0a1", "1.0a2"),
        ("1.0.post1", "1.0.post2"),
    ],
)
def test_pep440_prerelease_postrelease_ordering(earlier, later):
    assert Version(earlier) < Version(later)


def test_epoch_takes_precedence_in_ordering():
    assert Version("1!0.0") > Version("999.0")


def test_release_segments_are_compared_numerically():
    assert Version("1.10") > Version("1.2")


def test_local_versions_sort_after_public_version():
    assert Version("1.0") < Version("1.0+abc")


def test_local_string_segments_sort_before_integer_segments():
    assert Version("1.0+abc") < Version("1.0+1")


def test_local_versions_compare_lexicographically():
    assert Version("1.0+abc") < Version("1.0+def")


def test_local_versions_compare_numeric_segments_numerically():
    assert Version("1.0+abc.2") < Version("1.0+abc.10")


def test_local_versions_shorter_prefix_sorts_first():
    assert Version("1.0+abc") < Version("1.0+abc.1")


def test_versions_can_be_sorted():
    values = [
        Version("2.0"),
        Version("1.0"),
        Version("1.0rc1"),
        Version("1.0a1"),
        Version("1.0.dev1"),
        Version("1.0.post1"),
    ]
    assert [str(value) for value in sorted(values)] == [
        "1.0.dev1",
        "1.0a1",
        "1.0rc1",
        "1.0",
        "1.0.post1",
        "2.0",
    ]


@pytest.mark.parametrize(
    "operation",
    [
        lambda version: version < object(),
        lambda version: version <= object(),
        lambda version: version == object(),
        lambda version: version >= object(),
        lambda version: version > object(),
        lambda version: version != object(),
    ],
)
def test_comparison_with_unrelated_object(operation):
    with pytest.raises(TypeError):
        operation(Version("1.0"))


def test_comparison_with_string():
    version = Version("1.0")
    assert version != "1.0"
    assert not version == "1.0"


def test_hash_is_cached():
    version = Version("1.2.3")
    first_hash = hash(version)
    cached_hash = version._hash_cache
    assert cached_hash == first_hash
    assert hash(version) == first_hash
    assert version._hash_cache == cached_hash


def test_comparison_key_is_cached():
    version = Version("1.2.3")
    assert version._key_cache is None
    key = version._key
    assert version._key_cache is key
    assert version._key is key


def test_hash_populates_key_cache():
    version = Version("1.2.3")
    assert version._key_cache is None
    hash(version)
    assert version._key_cache is not None


def test_comparison_populates_key_caches():
    left = Version("1.0")
    right = Version("2.0")
    assert left._key_cache is None
    assert right._key_cache is None
    assert left < right
    assert left._key_cache is not None
    assert right._key_cache is not None


def test_from_parts_basic():
    version = Version.from_parts(release=(1, 2, 3))
    assert str(version) == "1.2.3"


def test_from_parts_all_components():
    version = Version.from_parts(
        epoch=2,
        release=(1, 2, 3),
        pre=("alpha", 4),
        post=5,
        dev=6,
        local="ABC.7",
    )
    assert str(version) == "2!1.2.3a4.post5.dev6+abc.7"


def test_from_parts_normalizes_prerelease():
    assert str(Version.from_parts(release=(1,), pre=("BETA", 2))) == "1b2"
    assert str(Version.from_parts(release=(1,), pre=("preview", 2))) == "1rc2"


def test_from_parts_optional_components_default_to_none():
    version = Version.from_parts(release=(1,))
    assert version.epoch == 0
    assert version.pre is None
    assert version.post is None
    assert version.dev is None
    assert version.local is None


@pytest.mark.parametrize("value", [-1, -10, 1.5, "1", None, object()])
def test_from_parts_rejects_invalid_epoch(value):
    with pytest.raises(InvalidVersion):
        Version.from_parts(epoch=value, release=(1,))


@pytest.mark.parametrize(
    "value",
    [
        None,
        (),
        [],
        (1, -1),
        (-1,),
        (1, 2.5),
        (1, "2"),
        "1.2",
        [1, 2],
    ],
)
def test_from_parts_rejects_invalid_release(value):
    with pytest.raises(InvalidVersion):
        Version.from_parts(release=value)


@pytest.mark.parametrize(
    "value",
    [
        ("invalid", 1),
        ("a", -1),
        ("b", 1.5),
        ("rc", "1"),
        ("alpha", -1),
        (1, 1),
        ("post", 1),
        ("dev", 1),
        ("a",),
        ("a", 1, 2),
        ["a", 1],
    ],
)
def test_from_parts_rejects_invalid_pre(value):
    with pytest.raises(InvalidVersion):
        Version.from_parts(release=(1,), pre=value)


@pytest.mark.parametrize("value", [-1, -2, 1.5, "1", object()])
def test_from_parts_rejects_invalid_post(value):
    with pytest.raises(InvalidVersion):
        Version.from_parts(release=(1,), post=value)


@pytest.mark.parametrize("value", [-1, -2, 1.5, "1", object()])
def test_from_parts_rejects_invalid_dev(value):
    with pytest.raises(InvalidVersion):
        Version.from_parts(release=(1,), dev=value)


@pytest.mark.parametrize(
    "value",
    [
        "",
        "abc..def",
        "abc--def",
        "abc__def",
        ".abc",
        "abc.",
        "-abc",
        "abc-",
        "_abc",
        "abc_",
        "abc+def",
        "abc def",
        "é",
        "你好",
        123,
        [],
    ],
)
def test_from_parts_rejects_invalid_local(value):
    with pytest.raises(InvalidVersion):
        Version.from_parts(release=(1,), local=value)


def test_from_parts_accepts_boolean_epoch():
    version = Version.from_parts(epoch=True, release=(1,))
    assert version.epoch == 1


def test_from_parts_accepts_boolean_release_component():
    version = Version.from_parts(release=(True,))
    assert version.release == (True,)


def test_from_parts_accepts_boolean_pre_number():
    version = Version.from_parts(release=(1,), pre=("a", True))
    assert version.pre == ("a", True)


def test_from_parts_accepts_boolean_post_and_dev():
    version = Version.from_parts(release=(1,), post=True, dev=False)
    assert version.post == 1
    assert version.dev == 0


def test_replace_without_changes_returns_same_object():
    version = Version("1.2.3")
    assert version.__replace__() is version


def test_replace_with_same_values_returns_same_object():
    version = Version("1.2.3")
    result = version.__replace__(
        epoch=0,
        release=(1, 2, 3),
        pre=None,
        post=None,
        dev=None,
        local=None,
    )
    assert result is version


def test_replace_changes_release():
    version = Version("1.2.3")
    result = version.__replace__(release=(2, 3, 4))
    assert str(result) == "2.3.4"
    assert str(version) == "1.2.3"
    assert result is not version


def test_replace_changes_all_components():
    version = Version("1.2.3")
    result = version.__replace__(
        epoch=2,
        release=(4, 5),
        pre=("beta", 1),
        post=2,
        dev=3,
        local="ABC.1",
    )
    assert str(result) == "2!4.5b1.post2.dev3+abc.1"


def test_replace_can_clear_components():
    version = Version("1!2.3a1.post2.dev3+abc")
    result = version.__replace__(
        epoch=0,
        pre=None,
        post=None,
        dev=None,
        local=None,
    )
    assert str(result) == "2.3"
    assert str(version) == "1!2.3a1.post2.dev3+abc"


def test_replace_normalizes_prerelease():
    version = Version("1.0")
    assert str(version.__replace__(pre=("ALPHA", 1))) == "1.0a1"
    assert str(version.__replace__(pre=("preview", 2))) == "1.0rc2"


@pytest.mark.parametrize(
    ("kwargs", "expected"),
    [
        ({"epoch": -1}, InvalidVersion),
        ({"release": ()}, InvalidVersion),
        ({"pre": ("invalid", 1)}, InvalidVersion),
        ({"post": -1}, InvalidVersion),
        ({"dev": -1}, InvalidVersion),
        ({"local": "bad..local"}, InvalidVersion),
    ],
)
def test_replace_validates_changed_fields(kwargs, expected):
    version = Version("1.0")
    with pytest.raises(expected):
        version.__replace__(**kwargs)


def test_replace_ignores_unrecognized_keyword():
    version = Version("1.0")
    with pytest.raises(KeyError):
        version.__replace__(unknown=1)


def test_replace_does_not_mutate_original_caches():
    version = Version("1.0")
    hash(version)
    original_key = version._key_cache
    original_hash = version._hash_cache
    result = version.__replace__(release=(2,))
    assert version._key_cache is original_key
    assert version._hash_cache == original_hash
    assert result._key_cache is None
    assert result._hash_cache is None


def test_version_getstate():
    version = Version("1!2.3a1.post2.dev3+abc.4")
    state = version.__getstate__()
    assert state == (
        1,
        (2, 3),
        ("a", 1),
        ("post", 2),
        ("dev", 3),
        ("abc", 4),
    )


def test_version_setstate_new_format():
    version = Version("1.0")
    state = (
        2,
        (3, 4),
        ("b", 1),
        ("post", 2),
        ("dev", 3),
        ("abc", 1),
    )
    version.__setstate__(state)
    assert str(version) == "2!3.4b1.post2.dev3+abc.1"
    assert version._key_cache is None
    assert version._hash_cache is None


def test_version_setstate_old_slots_format():
    version = Version("1.0")
    state = (
        None,
        {
            "_epoch": 2,
            "_release": (3, 4),
            "_pre": ("a", 1),
            "_post": ("post", 2),
            "_dev": ("dev", 3),
            "_local": ("abc", 1),
        },
    )
    version.__setstate__(state)
    assert str(version) == "2!3.4a1.post2.dev3+abc.1"


def test_version_setstate_old_slots_format_with_missing_optional_fields():
    version = Version("1.0")
    version.__setstate__((None, {"_epoch": 0, "_release": (2,)}))
    assert str(version) == "2"


def test_version_setstate_legacy_namedtuple_format():
    version = Version("1.0")
    old_version = _Version(
        epoch=2,
        release=(3, 4),
        dev=("dev", 3),
        pre=("b", 1),
        post=("post", 2),
        local=("abc", 1),
    )
    version.__setstate__({"_version": old_version, "_key": None})
    assert str(version) == "2!3.4b1.post2.dev3+abc.1"


def test_version_setstate_legacy_dict_without_optional_segments():
    version = Version("1.0")
    old_version = _Version(
        epoch=0,
        release=(2,),
        dev=None,
        pre=None,
        post=None,
        local=None,
    )
    version.__setstate__({"_version": old_version})
    assert str(version) == "2"


@pytest.mark.parametrize(
    "state",
    [
        None,
        [],
        (),
        (1,),
        (1, 2, 3),
        (None, []),
        (None, None),
        {},
        {"_key": None},
        {"_version": None},
        "invalid",
    ],
)
def test_version_setstate_rejects_invalid_state(state):
    version = Version("1.0")
    with pytest.raises(TypeError):
        version.__setstate__(state)


def test_version_setstate_resets_caches():
    version = Version("1.0")
    hash(version)
    assert version._key_cache is not None
    assert version._hash_cache is not None
    version.__setstate__((0, (2,), None, None, None, None))
    assert version._key_cache is None
    assert version._hash_cache is None


def test_version_pickle_round_trip():
    version = Version("1!2.3a1.post2.dev3+abc.4")
    restored = pickle.loads(pickle.dumps(version))
    assert restored == version
    assert str(restored) == str(version)
    assert restored._key_cache is None
    assert restored._hash_cache is None


def test_version_pickle_round_trip_after_hashing():
    version = Version("1.2.3")
    hash(version)
    restored = pickle.loads(pickle.dumps(version))
    assert restored == version
    assert hash(restored) == hash(version)


def test_version_pattern_matching():
    version = Version("1.2.3")
    match version:
        case Version(value):
            assert value == "1.2.3"
        case _:
            pytest.fail("Version did not match")


def test_private_version_property_getter():
    version = Version("1.2.3")
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        result = version._version
    assert result.epoch == 0
    assert result.release == (1, 2, 3)
    assert result.pre is None
    assert result.post is None
    assert result.dev is None
    assert result.local is None
    if version_module.sys.version_info < (3, 13):
        assert any(issubclass(item.category, DeprecationWarning) for item in caught)


def test_private_version_property_setter():
    version = Version("1.0")
    replacement = _Version(
        epoch=2,
        release=(3, 4),
        dev=("dev", 1),
        pre=("a", 2),
        post=("post", 3),
        local=("abc", 1),
    )
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        version._version = replacement
    assert version._epoch == 2
    assert version._release == (3, 4)
    assert version._dev == ("dev", 1)
    assert version._pre == ("a", 2)
    assert version._post == ("post", 3)
    assert version._local == ("abc", 1)
    assert version._key_cache is None
    assert version._hash_cache is None
    if version_module.sys.version_info < (3, 13):
        assert any(issubclass(item.category, DeprecationWarning) for item in caught)


def test_trimmed_release_from_version():
    version = Version("1.2.0.0")
    trimmed = _TrimmedRelease(version)
    assert trimmed.release == (1, 2)
    assert trimmed.epoch == version.epoch
    assert trimmed._pre == version._pre
    assert trimmed._post == version._post
    assert trimmed._dev == version._dev
    assert trimmed._local == version._local


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("1.0.0", (1,)),
        ("1.2.0.0", (1, 2)),
        ("0.0", (0,)),
        ("0.0.0.0", (0,)),
        ("1.2.3", (1, 2, 3)),
        ("1.2.3.0", (1, 2, 3)),
        ("1.2.0.3", (1, 2, 0, 3)),
    ],
)
def test_trimmed_release_trailing_zeroes(value, expected):
    assert _TrimmedRelease(value).release == expected


def test_trimmed_release_preserves_single_zero():
    assert _TrimmedRelease("0.0.0").release == (0,)


def test_trimmed_release_copies_cached_values():
    original = Version("1.2.3")
    hash(original)
    trimmed = _TrimmedRelease(original)
    assert trimmed._key_cache is original._key_cache
    assert trimmed._hash_cache == original._hash_cache


def test_parse_letter_version_with_number():
    assert _parse_letter_version("alpha", "2") == ("a", 2)
    assert _parse_letter_version("BETA", "3") == ("b", 3)
    assert _parse_letter_version("PREVIEW", "4") == ("rc", 4)


def test_parse_letter_version_without_number():
    assert _parse_letter_version("alpha", None) == ("a", 0)
    assert _parse_letter_version("post", None) == ("post", 0)


def test_parse_letter_version_without_letter_with_number():
    assert _parse_letter_version(None, "3") == ("post", 3)


def test_parse_letter_version_without_letter_or_number():
    assert _parse_letter_version(None, None) is None
    assert _parse_letter_version("", None) is None
    assert _parse_letter_version(None, 0) is None


def test_parse_letter_version_accepts_bytes_number():
    assert _parse_letter_version("a", b"3") == ("a", 3)


def test_parse_letter_version_invalid_number():
    with pytest.raises(ValueError):
        _parse_letter_version("a", "not-a-number")


def test_parse_letter_version_invalid_number_without_letter():
    with pytest.raises(ValueError):
        _parse_letter_version(None, "not-a-number")


def test_parse_local_version_none():
    assert _parse_local_version(None) is None


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("abc", ("abc",)),
        ("ABC", ("abc",)),
        ("abc.1", ("abc", 1)),
        ("abc-1", ("abc", 1)),
        ("abc_1", ("abc", 1)),
        ("abc.1.def", ("abc", 1, "def")),
        ("ABC-001_DEF", ("abc", 1, "def")),
        ("1.2.3", (1, 2, 3)),
        ("001", (1,)),
    ],
)
def test_parse_local_version(value, expected):
    assert _parse_local_version(value) == expected


def test_parse_local_version_empty_string():
    assert _parse_local_version("") == ("",)


def test_validate_epoch_defaults_none_and_zero():
    assert _validate_epoch(None) == 0
    assert _validate_epoch(0) == 0


@pytest.mark.parametrize("value", [0, 1, 10, True, False])
def test_validate_epoch_accepts_nonnegative_integers(value):
    assert _validate_epoch(value) == value


@pytest.mark.parametrize("value", [-1, -10, 1.5, "1", "0", object()])
def test_validate_epoch_rejects_invalid_values(value):
    with pytest.raises(InvalidVersion):
        _validate_epoch(value)


def test_validate_epoch_is_positional_only():
    with pytest.raises(TypeError):
        _validate_epoch(value=1)


def test_validate_release_defaults_none():
    assert _validate_release(None) == (0,)


@pytest.mark.parametrize(
    "value",
    [
        (0,),
        (1,),
        (1, 2, 3),
        (0, 0, 0),
        (True,),
    ],
)
def test_validate_release_accepts_valid_tuples(value):
    assert _validate_release(value) == value


@pytest.mark.parametrize(
    "value",
    [
        (),
        [],
        [1, 2],
        "1.2",
        (1, -1),
        (-1,),
        (1, 2.5),
        (1, "2"),
        None,
    ],
)
def test_validate_release_rejects_invalid_values(value):
    if value is None:
        assert _validate_release(value) == (0,)
    else:
        with pytest.raises(InvalidVersion):
            _validate_release(value)


def test_validate_release_is_positional_only():
    with pytest.raises(TypeError):
        _validate_release(value=(1,))


def test_validate_pre_accepts_none():
    assert _validate_pre(None) is None


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (("a", 0), ("a", 0)),
        (("alpha", 1), ("a", 1)),
        (("ALPHA", 2), ("a", 2)),
        (("b", 1), ("b", 1)),
        (("beta", 2), ("b", 2)),
        (("rc", 3), ("rc", 3)),
        (("preview", 4), ("rc", 4)),
        (("c", 5), ("rc", 5)),
    ],
)
def test_validate_pre_accepts_and_normalizes_values(value, expected):
    assert _validate_pre(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        ("invalid", 1),
        ("post", 1),
        ("dev", 1),
        ("a", -1),
        ("b", 1.5),
        ("rc", "1"),
        (1, 1),
        ("a",),
        ("a", 1, 2),
        ["a", 1],
        None,
    ],
)
def test_validate_pre_rejects_invalid_values(value):
    if value is None:
        assert _validate_pre(value) is None
    else:
        with pytest.raises(InvalidVersion):
            _validate_pre(value)


def test_validate_post_accepts_none():
    assert _validate_post(None) is None


@pytest.mark.parametrize("value", [0, 1, 10, True, False])
def test_validate_post_accepts_nonnegative_integer(value):
    assert _validate_post(value) == ("post", value)


@pytest.mark.parametrize("value", [-1, -10, 1.5, "1", object()])
def test_validate_post_rejects_invalid_values(value):
    with pytest.raises(InvalidVersion):
        _validate_post(value)


def test_validate_dev_accepts_none():
    assert _validate_dev(None) is None


@pytest.mark.parametrize("value", [0, 1, 10, True, False])
def test_validate_dev_accepts_nonnegative_integer(value):
    assert _validate_dev(value) == ("dev", value)


@pytest.mark.parametrize("value", [-1, -10, 1.5, "1", object()])
def test_validate_dev_rejects_invalid_values(value):
    with pytest.raises(InvalidVersion):
        _validate_dev(value)


def test_validate_local_accepts_none():
    assert _validate_local(None) is None


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("abc", ("abc",)),
        ("ABC", ("abc",)),
        ("abc.1", ("abc", 1)),
        ("abc-1", ("abc", 1)),
        ("abc_1", ("abc", 1)),
        ("1.2.3", (1, 2, 3)),
        ("abc.def.ghi", ("abc", "def", "ghi")),
    ],
)
def test_validate_local_accepts_valid_strings(value, expected):
    assert _validate_local(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        "",
        ".abc",
        "abc.",
        "abc..def",
        "abc--def",
        "abc__def",
        "abc+def",
        "abc def",
        "é",
        "你好",
        1,
        b"abc",
        [],
    ],
)
def test_validate_local_rejects_invalid_values(value):
    with pytest.raises(InvalidVersion):
        _validate_local(value)


def test_cmpkey_stable_fast_path():
    assert _cmpkey(0, (1, 0, 0), None, None, None, None) == (
        0,
        (1,),
        version_module._STABLE_SUFFIX,
    )


def test_cmpkey_strips_all_trailing_zeroes():
    assert _cmpkey(0, (0, 0), None, None, None, None) == (
        0,
        (),
        version_module._STABLE_SUFFIX,
    )


def test_cmpkey_keeps_release_without_trailing_zeroes():
    assert _cmpkey(0, (1, 2, 3), None, None, None, None) == (
        0,
        (1, 2, 3),
        version_module._STABLE_SUFFIX,
    )


def test_cmpkey_prerelease_ranks():
    assert _cmpkey(0, (1,), ("a", 1), None, None, None)[2][0] == 0
    assert _cmpkey(0, (1,), ("b", 1), None, None, None)[2][0] == 1
    assert _cmpkey(0, (1,), ("rc", 1), None, None, None)[2][0] == 2


def test_cmpkey_stable_rank():
    assert _cmpkey(0, (1,), None, None, None, None)[2][0] == 3


def test_cmpkey_dev_only_rank():
    key = _cmpkey(0, (1,), None, None, ("dev", 1), None)
    assert key[2][0] == -1


def test_cmpkey_pre_with_dev():
    key = _cmpkey(0, (1,), ("a", 1), None, ("dev", 2), None)
    assert key[2] == (0, 1, 0, 0, 0, 2)


def test_cmpkey_post_rank():
    without_post = _cmpkey(0, (1,), None, None, None, None)
    with_post = _cmpkey(0, (1,), None, ("post", 2), None, None)
    assert without_post[2][2:4] == (0, 0)
    assert with_post[2][2:4] == (1, 2)


def test_cmpkey_dev_rank():
    without_dev = _cmpkey(0, (1,), None, None, None, None)
    with_dev = _cmpkey(0, (1,), None, None, ("dev", 2), None)
    assert without_dev[2][4:6] == (1, 0)
    assert with_dev[2][4:6] == (0, 2)


def test_cmpkey_local_strings():
    key = _cmpkey(0, (1,), None, None, None, ("abc", "def"))
    assert key[3] == ((-1, "abc"), (-1, "def"))


def test_cmpkey_local_integers():
    key = _cmpkey(0, (1,), None, None, None, (1, 2))
    assert key[3] == ((1, ""), (2, ""))


def test_cmpkey_local_mixed_segments():
    key = _cmpkey(0, (1,), None, None, None, ("abc", 1, "def", 2))
    assert key[3] == ((-1, "abc"), (1, ""), (-1, "def"), (2, ""))


def test_cmpkey_includes_epoch():
    assert _cmpkey(2, (1,), None, None, None, None)[0] == 2


def test_cmpkey_local_none_returns_three_tuple():
    key = _cmpkey(0, (1,), ("a", 1), None, None, None)
    assert len(key) == 3


def test_cmpkey_local_present_returns_four_tuple():
    key = _cmpkey(0, (1,), None, None, None, ("abc",))
    assert len(key) == 4


def test_base_version_hash_and_comparison():
    class ExampleVersion(_BaseVersion):
        def __init__(self, key):
            self._key = key

    left = ExampleVersion((1,))
    right = ExampleVersion((2,))
    assert left < right
    assert left <= right
    assert right > left
    assert right >= left
    assert left != right
    assert left == ExampleVersion((1,))
    assert hash(left) == hash(ExampleVersion((1,)))


def test_base_version_comparison_with_unrelated_type():
    class ExampleVersion(_BaseVersion):
        def __init__(self, key):
            self._key = key

    version = ExampleVersion((1,))
    assert version.__lt__(object()) is NotImplemented
    assert version.__le__(object()) is NotImplemented
    assert version.__eq__(object()) is NotImplemented
    assert version.__ge__(object()) is NotImplemented
    assert version.__gt__(object()) is NotImplemented
    assert version.__ne__(object()) is NotImplemented


def test_version_comparison_with_base_version_subclass():
    class OtherVersion(_BaseVersion):
        def __init__(self, key):
            self._key = key

    version = Version("1.0")
    other = OtherVersion(version._key)
    assert version.__lt__(other) is NotImplemented
    assert version.__le__(other) is NotImplemented
    assert version.__eq__(other) is NotImplemented
    assert version.__ge__(other) is NotImplemented
    assert version.__gt__(other) is NotImplemented
    assert version.__ne__(other) is NotImplemented


def test_version_slots_prevent_instance_dictionary():
    version = Version("1.0")
    with pytest.raises(AttributeError):
        version.extra_attribute = True


def test_version_is_immutable_by_public_api():
    version = Version("1.0")
    with pytest.raises(AttributeError):
        version.extra_attribute = "value"


def test_version_hash_consistency_for_equal_versions():
    first = Version("1.0")
    second = Version("1.0.0")
    assert first == second
    assert hash(first) == hash(second)


def test_version_equality_is_reflexive():
    version = Version("1.2.3")
    assert version == version


def test_version_comparison_is_transitive():
    first = Version("1.0")
    second = Version("2.0")
    third = Version("3.0")
    assert first < second < third


def test_version_sorting_with_epochs_and_locals():
    values = [
        Version("1!1.0"),
        Version("1.0+2"),
        Version("1.0+abc"),
        Version("1.0"),
        Version("0!2.0"),
    ]
    assert [str(value) for value in sorted(values)] == [
        "1.0",
        "1.0+abc",
        "1.0+2",
        "2.0",
        "1!1.0",
    ]


def test_version_constructor_rejects_empty_release_components():
    for value in ("1..2", ".1", "1.", "1...2"):
        with pytest.raises(InvalidVersion):
            Version(value)


def test_version_constructor_accepts_leading_zeroes():
    assert str(Version("01.002.0003")) == "1.2.3"


def test_version_constructor_accepts_whitespace_around_version():
    assert str(Version("  1.2.3  ")) == "1.2.3"


def test_version_constructor_rejects_internal_whitespace():
    with pytest.raises(InvalidVersion):
        Version("1. 2.3")


def test_version_constructor_rejects_trailing_text():
    with pytest.raises(InvalidVersion):
        Version("1.2.3abcXYZ")


def test_version_constructor_rejects_unicode_digits():
    with pytest.raises(InvalidVersion):
        Version("１.２.３")


def test_version_local_version_is_case_insensitive():
    assert Version("1.0+ABC.DEF") == Version("1.0+abc.def")


def test_version_prerelease_aliases_are_equivalent():
    assert Version("1.0alpha1") == Version("1.0a1")
    assert Version("1.0beta1") == Version("1.0b1")
    assert Version("1.0preview1") == Version("1.0rc1")
    assert Version("1.0c1") == Version("1.0rc1")


def test_version_postrelease_aliases_are_equivalent():
    assert Version("1.0rev1") == Version("1.0.post1")
    assert Version("1.0r1") == Version("1.0.post1")
    assert Version("1.0-1") == Version("1.0.post1")


def test_version_development_release_aliases():
    assert Version("1.0dev1") == Version("1.0.dev1")


def test_version_release_property_keeps_trailing_zeroes():
    assert Version("1.2.0.0").release == (1, 2, 0, 0)


def test_version_comparison_ignores_trailing_release_zeroes():
    assert Version("1.2.0.0") == Version("1.2")


def test_version_base_version_keeps_release_trailing_zeroes():
    assert Version("1.2.0.0").base_version == "1.2.0.0"


def test_trimmed_release_is_used_only_for_comparison():
    original = Version("1.2.0.0")
    trimmed = _TrimmedRelease(original)
    assert original.release == (1, 2, 0, 0)
    assert trimmed.release == (1, 2)


def test_version_match_args():
    assert Version.__match_args__ == ("_str",)


def test_version_pattern_is_compiled():
    assert isinstance(Version._regex, re.Pattern)
    assert Version._regex.flags & re.IGNORECASE
    assert Version._regex.flags & re.VERBOSE


def test_version_pattern_is_not_anchored():
    match = re.search(
        version_module.VERSION_PATTERN,
        "prefix-1.2.3-suffix",
        re.VERBOSE | re.IGNORECASE,
    )
    assert match is not None
    assert match.group("release") == "1.2.3"


def test_version_pattern_supports_optional_v_prefix():
    assert re.fullmatch(
        version_module.VERSION_PATTERN,
        "v1.2.3",
        re.VERBOSE | re.IGNORECASE,
    )


def test_version_pattern_supports_epoch():
    match = re.fullmatch(
        version_module.VERSION_PATTERN,
        "2!1.2.3",
        re.VERBOSE | re.IGNORECASE,
    )
    assert match is not None
    assert match.group("epoch") == "2"


def test_version_pattern_supports_local_segment():
    match = re.fullmatch(
        version_module.VERSION_PATTERN,
        "1.2.3+abc.1",
        re.VERBOSE | re.IGNORECASE,
    )
    assert match is not None
    assert match.group("local") == "abc.1"


def test_version_pattern_rejects_invalid_local_segment():
    assert not re.fullmatch(
        version_module.VERSION_PATTERN,
        "1.2.3+abc..def",
        re.VERBOSE | re.IGNORECASE,
    )


def test_all_exports():
    assert version_module.__all__ == [
        "VERSION_PATTERN",
        "InvalidVersion",
        "Version",
        "normalize_pre",
        "parse",
    ]


def test_version_from_parts_does_not_require_epoch_argument():
    version = Version.from_parts(release=(1, 2))
    assert version.epoch == 0
    assert str(version) == "1.2"


def test_version_from_parts_requires_release():
    with pytest.raises(TypeError):
        Version.from_parts()


def test_version_from_parts_rejects_unknown_argument():
    with pytest.raises(TypeError):
        Version.from_parts(release=(1,), unknown=1)


def test_version_from_parts_returns_version_subclass():
    class CustomVersion(Version):
        pass

    version = CustomVersion.from_parts(release=(1, 2))
    assert isinstance(version, CustomVersion)


def test_replace_preserves_version_subclass():
    class CustomVersion(Version):
        pass

    version = CustomVersion("1.0")
    result = version.__replace__(release=(2,))
    assert isinstance(result, CustomVersion)


def test_replace_without_changes_preserves_subclass_identity():
    class CustomVersion(Version):
        pass

    version = CustomVersion("1.0")
    assert version.__replace__() is version


def test_trimmed_release_accepts_version_subclass():
    class CustomVersion(Version):
        pass

    version = CustomVersion("1.0.0")
    trimmed = _TrimmedRelease(version)
    assert trimmed.release == (1,)


def test_trimmed_release_rejects_invalid_string():
    with pytest.raises(InvalidVersion):
        _TrimmedRelease("invalid")


def test_version_setstate_rejects_two_item_state_with_non_dict():
    version = Version("1.0")
    with pytest.raises(TypeError):
        version.__setstate__((None, []))


def test_version_setstate_rejects_legacy_dict_without_version():
    version = Version("1.0")
    with pytest.raises(TypeError):
        version.__setstate__({"_key": (1,)})


def test_version_setstate_rejects_legacy_dict_with_none_version():
    version = Version("1.0")
    with pytest.raises(TypeError):
        version.__setstate__({"_version": None})


def test_version_state_round_trip_for_all_components():
    original = Version("3!4.5.6rc7.post8.dev9+abc.10")
    restored = Version("0")
    restored.__setstate__(original.__getstate__())
    assert restored == original
    assert str(restored) == str(original)


def test_version_hash_after_setstate():
    version = Version("1.0")
    version.__setstate__((1, (2, 3), None, None, None, None))
    assert hash(version) == hash(Version("1!2.3"))


def test_version_key_after_setstate():
    version = Version("1.0")
    version.__setstate__((1, (2, 3), None, None, None, None))
    assert version._key == Version("1!2.3")._key


def test_base_version_comparison_all_operators():
    class ExampleVersion(_BaseVersion):
        def __init__(self, key):
            self._key = key

    first = ExampleVersion((1,))
    second = ExampleVersion((2,))
    equal = ExampleVersion((1,))
    assert first < second
    assert first <= second
    assert second > first
    assert second >= first
    assert first == equal
    assert first != second
    assert not first != equal
    assert not first == second
