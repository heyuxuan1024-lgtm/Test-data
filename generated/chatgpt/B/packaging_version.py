
import pickle
import re
import warnings

import pytest

from packaging import version


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
        ("RC", "rc"),
        ("dev", "dev"),
        ("custom", "custom"),
        ("", ""),
    ],
)
def test_normalize_pre(value, expected):
    assert version.normalize_pre(value) == expected


def test_normalize_pre_requires_string():
    with pytest.raises(AttributeError):
        version.normalize_pre(None)


@pytest.mark.parametrize(
    "value",
    [
        "1",
        "1.0",
        "1.2.3",
        "v1.2.3",
        "1!2.3",
        "1.0a1",
        "1.0b2",
        "1.0rc3",
        "1.0.post1",
        "1.0.dev1",
        "1.0+local",
        "1.0rc1.post2.dev3+abc.1",
    ],
)
def test_parse_returns_version(value):
    result = version.parse(value)
    assert isinstance(result, version.Version)
    assert str(result) == str(version.Version(value))


def test_parse_invalid_version():
    with pytest.raises(version.InvalidVersion):
        version.parse("not-a-version")


@pytest.mark.parametrize(
    "value",
    [
        "",
        " ",
        "1..2",
        ".1",
        "1.",
        "1.2.",
        "1.2.3.4a",
        "1.2.3-",
        "1.2.3+",
        "1.2.3+abc..def",
        "1.2.3+abc!",
        "1.2.3+UPPER!",
        "1.2.3-alpha-beta",
        "1.2.3rc-",
        "1.2.3dev-",
        "01.02.03foo",
        "1.0.0.0.0.0.0.0.0.0!",
        "١.٢",
    ],
)
def test_invalid_version_strings(value):
    with pytest.raises(version.InvalidVersion):
        version.Version(value)


@pytest.mark.parametrize("value", [None, 1, 1.0, [], {}, object()])
def test_version_rejects_non_string_values(value):
    with pytest.raises(version.InvalidVersion):
        version.Version(value)


def test_version_simple_release_parsing():
    result = version.Version("1.2.3")
    assert result.epoch == 0
    assert result.release == (1, 2, 3)
    assert result.pre is None
    assert result.post is None
    assert result.dev is None
    assert result.local is None


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("1.0", "1.0"),
        ("v1.0", "1.0"),
        ("1.0.0", "1.0.0"),
        ("1!2.3", "1!2.3"),
        ("2!0.1", "2!0.1"),
        ("1.0alpha", "1.0a0"),
        ("1.0ALPHA1", "1.0a1"),
        ("1.0beta2", "1.0b2"),
        ("1.0preview3", "1.0rc3"),
        ("1.0pre4", "1.0rc4"),
        ("1.0c5", "1.0rc5"),
        ("1.0rev6", "1.0.post6"),
        ("1.0r7", "1.0.post7"),
        ("1.0post8", "1.0.post8"),
        ("1.0-9", "1.0.post9"),
        ("1.0dev10", "1.0.dev10"),
        ("1.0+ABC", "1.0+abc"),
        ("1.0+ABC.01-Def", "1.0+abc.1.def"),
        ("1.0+001", "1.0+1"),
    ],
)
def test_version_normalization(value, expected):
    assert str(version.Version(value)) == expected


def test_version_repr():
    result = version.Version("1.2.3")
    assert repr(result) == "<Version('1.2.3')>"


def test_version_str_and_repr_round_trip():
    original = version.Version("2!1.2.3rc1.post2.dev3+abc.4")
    assert version.Version(str(original)) == original
    assert "2!1.2.3rc1.post2.dev3+abc.4" in repr(original)


def test_version_properties():
    result = version.Version("2!1.3.5rc4.post6.dev7+ABC.8")
    assert result.epoch == 2
    assert result.release == (1, 3, 5)
    assert result.pre == ("rc", 4)
    assert result.post == 6
    assert result.dev == 7
    assert result.local == "abc.8"
    assert result.public == "2!1.3.5rc4.post6.dev7"
    assert result.base_version == "2!1.3.5"
    assert result.major == 1
    assert result.minor == 3
    assert result.micro == 5


def test_version_properties_without_optional_segments():
    result = version.Version("1.2")
    assert result.epoch == 0
    assert result.pre is None
    assert result.post is None
    assert result.dev is None
    assert result.local is None
    assert result.public == "1.2"
    assert result.base_version == "1.2"
    assert result.major == 1
    assert result.minor == 2
    assert result.micro == 0


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("1", (1, 0, 0)),
        ("1.2", (1, 2, 0)),
        ("1.2.3", (1, 2, 3)),
        ("0", (0, 0, 0)),
    ],
)
def test_release_component_properties(value, expected):
    result = version.Version(value)
    assert (result.major, result.minor, result.micro) == expected


@pytest.mark.parametrize(
    ("value", "pre", "post", "dev", "is_pre", "is_post", "is_dev"),
    [
        ("1.0", None, None, None, False, False, False),
        ("1.0a1", ("a", 1), None, None, True, False, False),
        ("1.0b1", ("b", 1), None, None, True, False, False),
        ("1.0rc1", ("rc", 1), None, None, True, False, False),
        ("1.0.post1", None, 1, None, False, True, False),
        ("1.0.dev1", None, None, 1, True, False, True),
        ("1.0a1.post2.dev3", ("a", 1), 2, 3, True, True, True),
    ],
)
def test_release_status_properties(
    value, pre, post, dev, is_pre, is_post, is_dev
):
    result = version.Version(value)
    assert result.pre == pre
    assert result.post == post
    assert result.dev == dev
    assert result.is_prerelease is is_pre
    assert result.is_postrelease is is_post
    assert result.is_devrelease is is_dev


def test_version_equality_and_normalized_release():
    assert version.Version("1.0") == version.Version("1.0.0")
    assert version.Version("1.0.0.0") == version.Version("1")
    assert version.Version("1.0") != version.Version("1.0.1")


def test_version_comparison_operators():
    lower = version.Version("1.0a1")
    stable = version.Version("1.0")
    higher = version.Version("1.1")
    assert lower < stable
    assert lower <= stable
    assert stable > lower
    assert stable >= lower
    assert stable == version.Version("1.0.0")
    assert stable != higher
    assert stable <= higher
    assert higher >= stable


def test_version_comparison_with_non_version():
    result = version.Version("1.0")
    assert result.__lt__(object()) is NotImplemented
    assert result.__le__(object()) is NotImplemented
    assert result.__eq__(object()) is NotImplemented
    assert result.__ne__(object()) is NotImplemented
    assert result.__gt__(object()) is NotImplemented
    assert result.__ge__(object()) is NotImplemented
    assert result != object()


def test_version_comparison_with_unrelated_type():
    result = version.Version("1.0")
    with pytest.raises(TypeError):
        _ = result < "1.1"
    with pytest.raises(TypeError):
        _ = result <= "1.1"
    with pytest.raises(TypeError):
        _ = result > "1.1"
    with pytest.raises(TypeError):
        _ = result >= "1.1"


def test_version_hash_consistency():
    first = version.Version("1.0")
    second = version.Version("1.0.0")
    assert hash(first) == hash(second)
    assert {first, second} == {first}


def test_version_hash_cache():
    result = version.Version("1.2.3")
    first_hash = hash(result)
    assert result._hash_cache == first_hash
    assert hash(result) == first_hash


def test_version_key_cache():
    result = version.Version("1.2.3")
    assert result._key_cache is None
    key = result._key
    assert result._key_cache == key
    assert result._key == key


def test_version_comparisons_populate_key_cache():
    first = version.Version("1.0")
    second = version.Version("2.0")
    assert first._key_cache is None
    assert second._key_cache is None
    assert first < second
    assert first._key_cache is not None
    assert second._key_cache is not None


def test_version_ordering_epochs():
    assert version.Version("1!0.1") > version.Version("999.9")
    assert version.Version("0!2.0") < version.Version("1!0.0")


def test_version_ordering_pre_releases():
    values = [
        "1.0.dev1",
        "1.0a1",
        "1.0a2",
        "1.0b1",
        "1.0rc1",
        "1.0",
    ]
    assert sorted(map(version.Version, reversed(values))) == list(
        map(version.Version, values)
    )


def test_version_ordering_post_and_dev_releases():
    values = [
        "1.0.dev1",
        "1.0",
        "1.0.post1.dev1",
        "1.0.post1",
        "1.0.post2",
    ]
    assert sorted(map(version.Version, reversed(values))) == list(
        map(version.Version, values)
    )


def test_version_local_ordering():
    assert version.Version("1.0+abc") < version.Version("1.0+1")
    assert version.Version("1.0+abc") < version.Version("1.0+abd")
    assert version.Version("1.0+1") < version.Version("1.0+2")
    assert version.Version("1.0") < version.Version("1.0+abc")


def test_version_local_segment_length_ordering():
    assert version.Version("1.0+abc") < version.Version("1.0+abc.1")


def test_version_from_parts_basic():
    result = version.Version.from_parts(release=(1, 2, 3))
    assert isinstance(result, version.Version)
    assert str(result) == "1.2.3"


def test_version_from_parts_all_parts():
    result = version.Version.from_parts(
        epoch=2,
        release=(1, 2, 3),
        pre=("BETA", 4),
        post=5,
        dev=6,
        local="ABC.7",
    )
    assert str(result) == "2!1.2.3b4.post5.dev6+abc.7"
    assert result.epoch == 2
    assert result.pre == ("b", 4)
    assert result.post == 5
    assert result.dev == 6
    assert result.local == "abc.7"


def test_version_from_parts_normalizes_pre_release():
    assert str(version.Version.from_parts(release=(1,), pre=("alpha", 1))) == "1a1"
    assert str(version.Version.from_parts(release=(1,), pre=("preview", 2))) == "1rc2"
    assert str(version.Version.from_parts(release=(1,), pre=("c", 3))) == "1rc3"


@pytest.mark.parametrize("epoch", [-1, 1.5, "1", None])
def test_from_parts_invalid_epoch(epoch):
    if epoch is None:
        result = version.Version.from_parts(release=(1,), epoch=epoch)
        assert result.epoch == 0
    else:
        with pytest.raises(version.InvalidVersion):
            version.Version.from_parts(release=(1,), epoch=epoch)


@pytest.mark.parametrize(
    "release",
    [
        None,
        (),
        [],
        [1, 2],
        "1.2",
        (1, -1),
        (-1,),
        (1, 2.5),
        (True, 1),
    ],
)
def test_from_parts_invalid_release(release):
    with pytest.raises(version.InvalidVersion):
        version.Version.from_parts(release=release)


@pytest.mark.parametrize(
    "pre",
    [
        ("x", 1),
        ("a", -1),
        ("b", 1.5),
        (1, 1),
        ("a", "1"),
        ("a",),
        ("a", 1, 2),
        [],
    ],
)
def test_from_parts_invalid_pre(pre):
    with pytest.raises(version.InvalidVersion):
        version.Version.from_parts(release=(1,), pre=pre)


@pytest.mark.parametrize("post", [-1, 1.5, "1", []])
def test_from_parts_invalid_post(post):
    with pytest.raises(version.InvalidVersion):
        version.Version.from_parts(release=(1,), post=post)


@pytest.mark.parametrize("dev", [-1, 1.5, "1", []])
def test_from_parts_invalid_dev(dev):
    with pytest.raises(version.InvalidVersion):
        version.Version.from_parts(release=(1,), dev=dev)


@pytest.mark.parametrize(
    "local",
    [
        "",
        "abc..def",
        ".abc",
        "abc.",
        "abc+def",
        "abc def",
        "abc!",
        "你好",
        "abc--",
        "abc__",
    ],
)
def test_from_parts_invalid_local(local):
    with pytest.raises(version.InvalidVersion):
        version.Version.from_parts(release=(1,), local=local)


@pytest.mark.parametrize("local", ["abc", "ABC", "abc.1", "abc-1_def", "001"])
def test_from_parts_valid_local(local):
    result = version.Version.from_parts(release=(1,), local=local)
    assert result.local is not None


def test_from_parts_accepts_none_optional_parts():
    result = version.Version.from_parts(
        release=(1,), pre=None, post=None, dev=None, local=None
    )
    assert str(result) == "1"


def test_from_parts_requires_release():
    with pytest.raises(TypeError):
        version.Version.from_parts()


def test_version_replace_no_changes_returns_same_instance():
    result = version.Version("1.2.3")
    assert result.__replace__() is result


def test_version_replace_unknown_keyword_is_ignored():
    result = version.Version("1.2.3")
    assert result.__replace__(unknown="value") is result


def test_version_replace_changes_release():
    original = version.Version("1.2.3")
    updated = original.__replace__(release=(4, 5))
    assert updated is not original
    assert str(updated) == "4.5"
    assert str(original) == "1.2.3"


def test_version_replace_changes_all_parts():
    original = version.Version("1.2.3")
    updated = original.__replace__(
        epoch=2,
        release=(4, 5),
        pre=("alpha", 1),
        post=2,
        dev=3,
        local="ABC.4",
    )
    assert str(updated) == "2!4.5a1.post2.dev3+abc.4"


def test_version_replace_clears_optional_parts():
    original = version.Version("1!2.3a1.post2.dev3+abc")
    updated = original.__replace__(
        epoch=0,
        pre=None,
        post=None,
        dev=None,
        local=None,
    )
    assert str(updated) == "2.3"


def test_version_replace_same_values_returns_same_instance():
    original = version.Version("1.2.3a1.post2.dev3+abc")
    updated = original.__replace__(
        epoch=0,
        release=(1, 2, 3),
        pre=("a", 1),
        post=2,
        dev=3,
        local="abc",
    )
    assert updated is original


@pytest.mark.parametrize(
    ("kwargs", "expected_exception"),
    [
        ({"epoch": -1}, version.InvalidVersion),
        ({"release": ()}, version.InvalidVersion),
        ({"pre": ("invalid", 1)}, version.InvalidVersion),
        ({"post": -1}, version.InvalidVersion),
        ({"dev": -1}, version.InvalidVersion),
        ({"local": "invalid local"}, version.InvalidVersion),
    ],
)
def test_version_replace_invalid_values(kwargs, expected_exception):
    with pytest.raises(expected_exception):
        version.Version("1.0").__replace__(**kwargs)


def test_version_getstate():
    result = version.Version("1!2.3a1.post2.dev3+abc.4")
    state = result.__getstate__()
    assert state == (
        1,
        (2, 3),
        ("a", 1),
        ("post", 2),
        ("dev", 3),
        ("abc", 4),
    )


def test_version_setstate_new_tuple_format():
    result = version.Version.__new__(version.Version)
    state = (
        1,
        (2, 3),
        ("b", 4),
        ("post", 5),
        ("dev", 6),
        ("abc", 7),
    )
    result.__setstate__(state)
    assert str(result) == "1!2.3b4.post5.dev6+abc.7"
    assert result._key_cache is None
    assert result._hash_cache is None


def test_version_setstate_legacy_slot_dict_format():
    result = version.Version.__new__(version.Version)
    state = (
        None,
        {
            "_epoch": 2,
            "_release": (3, 4),
            "_pre": ("rc", 1),
            "_post": ("post", 2),
            "_dev": ("dev", 3),
            "_local": ("abc", 4),
        },
    )
    result.__setstate__(state)
    assert str(result) == "2!3.4rc1.post2.dev3+abc.4"


def test_version_setstate_legacy_slot_dict_missing_optional_values():
    result = version.Version.__new__(version.Version)
    result.__setstate__((None, {"_epoch": 0, "_release": (1, 2)}))
    assert str(result) == "1.2"
    assert result.pre is None
    assert result.post is None
    assert result.dev is None
    assert result.local is None


def test_version_setstate_legacy_namedtuple_dict():
    original = version.Version("1!2.3a1.post2.dev3+abc")
    legacy = {
        "_version": original._version,
        "_key": None,
    }
    result = version.Version.__new__(version.Version)
    result.__setstate__(legacy)
    assert str(result) == str(original)


def test_version_setstate_rejects_invalid_state():
    result = version.Version.__new__(version.Version)
    with pytest.raises(TypeError, match="Cannot restore Version"):
        result.__setstate__(None)


@pytest.mark.parametrize(
    "state",
    [
        (),
        (1,),
        (1, 2, 3),
        (None, []),
        (None, {}),
        {"_key": None},
        "invalid",
    ],
)
def test_version_setstate_rejects_unsupported_states(state):
    result = version.Version.__new__(version.Version)
    with pytest.raises(TypeError):
        result.__setstate__(state)


def test_version_pickle_round_trip():
    original = version.Version("2!1.2.3rc1.post2.dev3+abc.4")
    restored = pickle.loads(pickle.dumps(original))
    assert restored == original
    assert str(restored) == str(original)
    assert restored.__getstate__() == original.__getstate__()


def test_version_pickle_round_trip_without_optional_parts():
    original = version.Version("1.2.3")
    restored = pickle.loads(pickle.dumps(original))
    assert restored == original
    assert restored._key_cache is None
    assert restored._hash_cache is None


def test_version_private_property_warns():
    result = version.Version("1.2.3")
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        value = result._version
    assert value.epoch == 0
    assert value.release == (1, 2, 3)
    assert any(item.category is DeprecationWarning for item in caught)


def test_version_private_property_setter_warns_and_resets_caches():
    result = version.Version("1.2.3")
    hash(result)
    _ = result._key
    replacement = version.Version("4.5.6")._version
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        result._version = replacement
    assert str(result) == "4.5.6"
    assert result._key_cache is None
    assert result._hash_cache is None
    assert len(caught) >= 1
    assert all(item.category is DeprecationWarning for item in caught)


def test_version_slots_and_match_args():
    assert version.Version.__match_args__ == ("_str",)
    assert "_release" in version.Version.__slots__
    assert "_key_cache" in version.Version.__slots__


def test_version_pattern_is_compilable():
    compiled = re.compile(
        version.VERSION_PATTERN,
        re.VERBOSE | re.IGNORECASE,
    )
    assert compiled.search("release-1.2.3") is not None
    assert compiled.search("release-1.2.3") .group("release") == "1.2.3"


def test_version_pattern_is_not_anchored():
    compiled = re.compile(
        version.VERSION_PATTERN,
        re.VERBOSE | re.IGNORECASE,
    )
    assert compiled.search("prefix-1.2.3-suffix") is not None


def test_validate_epoch():
    assert version._validate_epoch(0) == 0
    assert version._validate_epoch(3) == 3
    assert version._validate_epoch(None) == 0
    assert version._validate_epoch(False) == 0
    assert version._validate_epoch(True) == 1


@pytest.mark.parametrize("value", [-1, 1.5, "1", [], {}])
def test_validate_epoch_invalid(value):
    with pytest.raises(version.InvalidVersion):
        version._validate_epoch(value)


def test_validate_release():
    assert version._validate_release(None) == (0,)
    assert version._validate_release((1, 2, 3)) == (1, 2, 3)
    assert version._validate_release((0,)) == (0,)


@pytest.mark.parametrize(
    "value",
    [
        (),
        [],
        [1],
        "1",
        (-1,),
        (1, -1),
        (1.5,),
        (None,),
    ],
)
def test_validate_release_invalid(value):
    with pytest.raises(version.InvalidVersion):
        version._validate_release(value)


def test_validate_pre():
    assert version._validate_pre(None) is None
    assert version._validate_pre(("alpha", 1)) == ("a", 1)
    assert version._validate_pre(("BETA", 2)) == ("b", 2)
    assert version._validate_pre(("preview", 3)) == ("rc", 3)
    assert version._validate_pre(("c", 4)) == ("rc", 4)
    assert version._validate_pre(("rc", 0)) == ("rc", 0)


@pytest.mark.parametrize(
    "value",
    [
        ("invalid", 1),
        ("a", -1),
        ("b", 1.5),
        (1, 1),
        ("a", "1"),
        ("a",),
        ("a", 1, 2),
        [],
        {},
    ],
)
def test_validate_pre_invalid(value):
    with pytest.raises(version.InvalidVersion):
        version._validate_pre(value)


def test_validate_post():
    assert version._validate_post(None) is None
    assert version._validate_post(0) == ("post", 0)
    assert version._validate_post(3) == ("post", 3)
    assert version._validate_post(True) == ("post", True)


@pytest.mark.parametrize("value", [-1, 1.5, "1", [], {}])
def test_validate_post_invalid(value):
    with pytest.raises(version.InvalidVersion):
        version._validate_post(value)


def test_validate_dev():
    assert version._validate_dev(None) is None
    assert version._validate_dev(0) == ("dev", 0)
    assert version._validate_dev(3) == ("dev", 3)


@pytest.mark.parametrize("value", [-1, 1.5, "1", [], {}])
def test_validate_dev_invalid(value):
    with pytest.raises(version.InvalidVersion):
        version._validate_dev(value)


def test_validate_local():
    assert version._validate_local(None) is None
    assert version._validate_local("ABC.1") == ("abc", 1)
    assert version._validate_local("foo-bar_baz") == ("foo", "bar", "baz")
    assert version._validate_local("001") == (1,)


@pytest.mark.parametrize(
    "value",
    [
        "",
        1,
        [],
        {},
        "foo..bar",
        ".foo",
        "foo.",
        "foo bar",
        "foo+bar",
        "foo!",
        "é",
    ],
)
def test_validate_local_invalid(value):
    with pytest.raises(version.InvalidVersion):
        version._validate_local(value)


def test_parse_letter_version_normalizes_aliases():
    assert version._parse_letter_version("alpha", "1") == ("a", 1)
    assert version._parse_letter_version("BETA", "2") == ("b", 2)
    assert version._parse_letter_version("preview", "3") == ("rc", 3)
    assert version._parse_letter_version("c", "4") == ("rc", 4)
    assert version._parse_letter_version("rev", "5") == ("post", 5)
    assert version._parse_letter_version("r", "6") == ("post", 6)


def test_parse_letter_version_implicit_zero():
    assert version._parse_letter_version("a", None) == ("a", 0)
    assert version._parse_letter_version("b", "") == ("b", 0)


def test_parse_letter_version_implicit_post():
    assert version._parse_letter_version(None, "3") == ("post", 3)


def test_parse_letter_version_without_letter_or_number():
    assert version._parse_letter_version(None, None) is None
    assert version._parse_letter_version("", "") is None


def test_parse_letter_version_invalid_number():
    with pytest.raises(ValueError):
        version._parse_letter_version("a", "invalid")
    with pytest.raises(ValueError):
        version._parse_letter_version(None, "invalid")


def test_parse_local_version():
    assert version._parse_local_version(None) is None
    assert version._parse_local_version("abc.1.TWO") == ("abc", 1, "two")
    assert version._parse_local_version("abc-2_def") == ("abc", 2, "def")
    assert version._parse_local_version("001") == (1,)


def test_cmpkey_stable_release_trims_trailing_zeros():
    assert version._cmpkey(0, (1, 0, 0), None, None, None, None) == (
        0,
        (1,),
        version._STABLE_SUFFIX,
    )


def test_cmpkey_stable_release_fast_path():
    result = version._cmpkey(2, (1, 2, 0), None, None, None, None)
    assert result == (2, (1, 2), version._STABLE_SUFFIX)


def test_cmpkey_pre_release():
    result = version._cmpkey(0, (1,), ("a", 1), None, None, None)
    assert result[2][0:2] == (0, 1)


def test_cmpkey_beta_release():
    result = version._cmpkey(0, (1,), ("b", 2), None, None, None)
    assert result[2][0:2] == (1, 2)


def test_cmpkey_rc_release():
    result = version._cmpkey(0, (1,), ("rc", 3), None, None, None)
    assert result[2][0:2] == (2, 3)


def test_cmpkey_dev_only_release():
    result = version._cmpkey(0, (1,), None, None, ("dev", 1), None)
    assert result[2][0:2] == (version._PRE_RANK_DEV_ONLY, 0)


def test_cmpkey_post_release():
    result = version._cmpkey(0, (1,), None, ("post", 2), None, None)
    assert result[2][2:4] == (1, 2)


def test_cmpkey_dev_rank():
    without_dev = version._cmpkey(0, (1,), None, None, None, None)
    with_dev = version._cmpkey(0, (1,), None, None, ("dev", 1), None)
    assert without_dev[2][4] == 1
    assert with_dev[2][4] == 0


def test_cmpkey_local_string_segments():
    result = version._cmpkey(0, (1,), None, None, None, ("ubuntu",))
    assert result[3] == ((version._LOCAL_STR_RANK, "ubuntu"),)


def test_cmpkey_local_integer_segments():
    result = version._cmpkey(0, (1,), None, None, None, (1, 2))
    assert result[3] == ((1, ""), (2, ""))


def test_cmpkey_mixed_local_segments():
    result = version._cmpkey(0, (1,), None, None, None, ("abc", 2))
    assert result[3] == ((version._LOCAL_STR_RANK, "abc"), (2, ""))


def test_cmpkey_local_none_returns_three_part_key():
    result = version._cmpkey(0, (1,), ("a", 1), None, None, None)
    assert len(result) == 3


def test_cmpkey_local_value_returns_four_part_key():
    result = version._cmpkey(0, (1,), None, None, None, ("abc",))
    assert len(result) == 4


def test_trimmed_release_removes_trailing_zeroes():
    result = version._TrimmedRelease("1.0.0")
    assert result.release == (1,)


def test_trimmed_release_keeps_single_zero():
    result = version._TrimmedRelease("0.0")
    assert result.release == (0,)


def test_trimmed_release_without_trailing_zeroes():
    result = version._TrimmedRelease("1.2.3")
    assert result.release == (1, 2, 3)


def test_trimmed_release_copies_version_fields():
    original = version.Version("1.2.0a1+abc")
    result = version._TrimmedRelease(original)
    assert result.release == (1, 2)
    assert result.epoch == original.epoch
    assert result.pre == original.pre
    assert result.local == original.local
    assert result._key_cache is original._key_cache
    assert result._hash_cache is original._hash_cache


def test_trimmed_release_comparison_uses_trimmed_release():
    assert version._TrimmedRelease("1.0.0") == version.Version("1")
    assert version._TrimmedRelease("1.2.0") == version.Version("1.2")


def test_module_dir():
    assert dir(version) == version.__all__
    assert version.__all__ == [
        "VERSION_PATTERN",
        "InvalidVersion",
        "Version",
        "normalize_pre",
        "parse",
    ]


def test_version_pattern_matches_supported_versions():
    pattern = re.compile(
        version.VERSION_PATTERN,
        re.VERBOSE | re.IGNORECASE,
    )
    for value in [
        "1.0",
        "v1.2.3",
        "1!2.0",
        "1.0a1",
        "1.0b2",
        "1.0rc3",
        "1.0.post1",
        "1.0.dev1",
        "1.0+abc.1",
    ]:
        assert pattern.fullmatch(value) is not None


def test_version_pattern_does_not_match_invalid_versions():
    pattern = re.compile(
        version.VERSION_PATTERN,
        re.VERBOSE | re.IGNORECASE,
    )
    for value in ["", "abc", "1..2", "1.0+", "1.0+abc..def"]:
        assert pattern.fullmatch(value) is None


def test_version_is_immutable_in_practice():
    result = version.Version("1.2.3")
    with pytest.raises(AttributeError):
        result.new_attribute = "value"


def test_version_match_args_pattern_matching():
    result = version.Version("1.2.3")
    match result:
        case version.Version(value):
            assert value == "1.2.3"
        case _:
            pytest.fail("Version pattern matching did not match")


def test_version_sorting_mixed_versions():
    values = [
        "2.0",
        "1.0",
        "1.0.post1",
        "1.0rc1",
        "1.0b1",
        "1.0a1",
        "1.0.dev1",
        "1!0.1",
    ]
    expected = [
        "1.0.dev1",
        "1.0a1",
        "1.0b1",
        "1.0rc1",
        "1.0",
        "1.0.post1",
        "2.0",
        "1!0.1",
    ]
    assert [str(item) for item in sorted(map(version.Version, values))] == expected


def test_version_local_case_insensitive_equality():
    assert version.Version("1.0+ABC") == version.Version("1.0+abc")


def test_version_local_numeric_segments_normalize():
    assert version.Version("1.0+abc.001") == version.Version("1.0+abc.1")


def test_version_public_and_base_version_with_epoch_and_local():
    result = version.Version("3!1.2.3a1+local")
    assert result.public == "3!1.2.3a1"
    assert result.base_version == "3!1.2.3"


def test_version_from_parts_with_zero_release():
    result = version.Version.from_parts(release=(0, 0, 0))
    assert str(result) == "0.0.0"
    assert result.release == (0, 0, 0)


def test_version_comparison_local_numeric_and_string():
    assert version.Version("1.0+abc") < version.Version("1.0+1")
    assert version.Version("1.0+1") < version.Version("1.0+1.1")
    assert version.Version("1.0+1.1") < version.Version("1.0+2")


def test_version_comparison_dev_only_before_alpha():
    assert version.Version("1.0.dev1") < version.Version("1.0a1")


def test_version_comparison_post_release_after_stable():
    assert version.Version("1.0") < version.Version("1.0.post1")


def test_version_comparison_dev_release_before_final():
    assert version.Version("1.0.dev1") < version.Version("1.0")


def test_version_hash_after_comparison():
    first = version.Version("1.0")
    second = version.Version("1.0.0")
    assert first == second
    assert hash(first) == hash(second)


def test_version_hash_after_key_property():
    result = version.Version("1.2.3")
    _ = result._key
    assert hash(result) == hash(result._key)


def test_version_setstate_resets_existing_caches():
    result = version.Version("1.2.3")
    hash(result)
    _ = result._key
    assert result._key_cache is not None
    assert result._hash_cache is not None
    result.__setstate__((0, (4, 5), None, None, None, None))
    assert result._key_cache is None
    assert result._hash_cache is None
    assert str(result) == "4.5"
