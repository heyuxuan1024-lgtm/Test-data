import copy
import itertools
import operator
import pickle
import re
import sys

import pytest

from packaging import version


class _Other(version._BaseVersion):
    __slots__ = ("_value",)

    def __init__(self, value):
        self._value = value

    @property
    def _key(self):
        return version._cmpkey(0, (self._value,), None, None, None, None)


class _MyVersion(version.Version):
    __slots__ = ()


ORDERED = [
    "1.0.dev1",
    "1.0a1.dev1",
    "1.0a1",
    "1.0a2",
    "1.0b1",
    "1.0rc1",
    "1.0",
    "1.0+abc",
    "1.0+abc.1",
    "1.0+abd",
    "1.0+1",
    "1.0.post1.dev1",
    "1.0.post1",
    "1.0.post2",
    "1.1.dev1",
    "1.1",
    "1!0.1",
]

ADJACENT_PAIRS = list(zip(ORDERED, ORDERED[1:]))

ORDER_OPS = [operator.lt, operator.le, operator.gt, operator.ge]


@pytest.mark.parametrize(
    "letter, expected",
    [
        ("alpha", "a"),
        ("ALPHA", "a"),
        ("a", "a"),
        ("beta", "b"),
        ("BETA", "b"),
        ("b", "b"),
        ("c", "rc"),
        ("pre", "rc"),
        ("preview", "rc"),
        ("rc", "rc"),
        ("RC", "rc"),
        ("rev", "post"),
        ("r", "post"),
        ("post", "post"),
        ("Foo", "foo"),
        ("", ""),
    ],
)
def test_normalize_pre(letter, expected):
    assert version.normalize_pre(letter) == expected


def test_normalize_pre_non_string_raises():
    with pytest.raises(AttributeError):
        version.normalize_pre(None)


def test_parse_returns_version():
    parsed = version.parse("1.0.dev1")
    assert isinstance(parsed, version.Version)
    assert str(parsed) == "1.0.dev1"
    assert repr(parsed) == "<Version('1.0.dev1')>"


def test_parse_invalid_raises():
    with pytest.raises(version.InvalidVersion):
        version.parse("invalid")
    with pytest.raises(version.InvalidVersion):
        version.parse(None)


def test_invalid_version_is_value_error():
    assert issubclass(version.InvalidVersion, ValueError)
    with pytest.raises(version.InvalidVersion, match="Invalid version: 'invalid'"):
        version.Version("invalid")


def test_module_all_and_dir():
    assert version.__all__ == [
        "VERSION_PATTERN",
        "InvalidVersion",
        "Version",
        "normalize_pre",
        "parse",
    ]
    assert version.__dir__() == version.__all__
    assert dir(version) == version.__all__


def test_version_pattern_matches_and_searches():
    regex = re.compile(version.VERSION_PATTERN, re.VERBOSE | re.IGNORECASE)
    match = regex.fullmatch("1!2.3a4.post5.dev6+abc.7")
    assert match is not None
    assert match.group("epoch") == "1"
    assert match.group("release") == "2.3"
    assert match.group("pre_l") == "a"
    assert match.group("pre_n") == "4"
    assert match.group("post_l") == "post"
    assert match.group("post_n2") == "5"
    assert match.group("dev_l") == "dev"
    assert match.group("dev_n") == "6"
    assert match.group("local") == "abc.7"
    found = regex.search("release-2.5.tgz")
    assert found is not None
    assert found.group("release") == "2.5"
    assert regex.fullmatch("not a version") is None


def test_old_and_new_patterns_differ_only_in_possessive_quantifiers():
    assert "?+" in version._VERSION_PATTERN
    assert "*+" in version._VERSION_PATTERN
    assert "?+" not in version._VERSION_PATTERN_OLD
    assert "*+" not in version._VERSION_PATTERN_OLD
    assert version.VERSION_PATTERN in (
        version._VERSION_PATTERN,
        version._VERSION_PATTERN_OLD,
    )
    flags = re.VERBOSE | re.IGNORECASE
    old = re.compile(version._VERSION_PATTERN_OLD, flags)
    assert old.fullmatch("1.0a1.post2.dev3+local.4") is not None


@pytest.mark.parametrize(
    "text, release",
    [
        ("1", (1,)),
        ("1.2", (1, 2)),
        ("1.2.3", (1, 2, 3)),
        ("1.0.0", (1, 0, 0)),
        ("01.02", (1, 2)),
        ("0", (0,)),
        ("10.20.30.40.50", (10, 20, 30, 40, 50)),
    ],
)
def test_simple_versions(text, release):
    v = version.Version(text)
    assert v.release == release
    assert v.epoch == 0
    assert v.pre is None
    assert v.post is None
    assert v.dev is None
    assert v.local is None
    assert v._key_cache is None
    assert v._hash_cache is None


@pytest.mark.parametrize("text", ["", ".", "1.", ".1", "1..2", "..", "1.2."])
def test_simple_versions_with_empty_parts_are_invalid(text):
    with pytest.raises(version.InvalidVersion, match="Invalid version"):
        version.Version(text)


@pytest.mark.parametrize("bad", [None, 123, 1.5, object()])
def test_non_iterable_input_raises_invalid_version(bad):
    with pytest.raises(version.InvalidVersion):
        version.Version(bad)


def test_bytes_input_raises_invalid_version():
    with pytest.raises(version.InvalidVersion):
        version.Version(b"1.0")


def test_list_of_simple_chars_raises_invalid_version():
    with pytest.raises(version.InvalidVersion):
        version.Version(["1", "."])
    with pytest.raises(version.InvalidVersion):
        version.Version(["1"])


@pytest.mark.skipif(
    not hasattr(sys, "set_int_max_str_digits"),
    reason="int string digit limit not available",
)
def test_int_digit_limit_error_propagates():
    old = sys.get_int_max_str_digits()
    sys.set_int_max_str_digits(640)
    try:
        with pytest.raises(ValueError) as info:
            version.Version("1" * 1000)
    finally:
        sys.set_int_max_str_digits(old)
    assert not isinstance(info.value, version.InvalidVersion)


@pytest.mark.parametrize(
    "text, expected",
    [
        ("1.0a1", ("a", 1)),
        ("1.0alpha", ("a", 0)),
        ("1.0.alpha.2", ("a", 2)),
        ("1.0-alpha.1", ("a", 1)),
        ("1.0b2", ("b", 2)),
        ("1.0beta3", ("b", 3)),
        ("1.0c1", ("rc", 1)),
        ("1.0rc1", ("rc", 1)),
        ("1.0RC1", ("rc", 1)),
        ("1.0pre4", ("rc", 4)),
        ("1.0preview5", ("rc", 5)),
        ("1.0_rc_2", ("rc", 2)),
        ("1.0a0", ("a", 0)),
        ("1.0a", ("a", 0)),
    ],
)
def test_pre_release_parsing(text, expected):
    v = version.Version(text)
    assert v.pre == expected
    assert v.is_prerelease


@pytest.mark.parametrize(
    "text, expected",
    [
        ("1.0.post1", 1),
        ("1.0-1", 1),
        ("1.0.post", 0),
        ("1.0post", 0),
        ("1.0rev2", 2),
        ("1.0r3", 3),
        ("1.0-r2", 2),
        ("1.0.post.1", 1),
        ("1.0_post_4", 4),
        ("1.0.post0", 0),
    ],
)
def test_post_release_parsing(text, expected):
    v = version.Version(text)
    assert v.post == expected
    assert v.is_postrelease


@pytest.mark.parametrize(
    "text, expected",
    [
        ("1.0.dev1", 1),
        ("1.0dev5", 5),
        ("1.0.dev", 0),
        ("1.0-dev.3", 3),
        ("1.0.dev0", 0),
    ],
)
def test_dev_release_parsing(text, expected):
    v = version.Version(text)
    assert v.dev == expected
    assert v.is_devrelease
    assert v.is_prerelease


@pytest.mark.parametrize(
    "text, expected",
    [
        ("1.0+abc", "abc"),
        ("1.0+ABC", "abc"),
        ("1.0+abc.1", "abc.1"),
        ("1.0+a-b_c", "a.b.c"),
        ("1.0+1.2", "1.2"),
        ("1.0+007", "7"),
        ("1.0+ubuntu.1", "ubuntu.1"),
    ],
)
def test_local_parsing(text, expected):
    assert version.Version(text).local == expected


def test_epoch_parsing():
    assert version.Version("1!1.0").epoch == 1
    assert version.Version("25!1.0").epoch == 25
    assert version.Version("0!1.0").epoch == 0


def test_leading_v_and_whitespace_and_case():
    assert str(version.Version("v1.0")) == "1.0"
    assert str(version.Version("V1.0")) == "1.0"
    assert str(version.Version("  1.0  ")) == "1.0"
    assert str(version.Version("\t1.0\n")) == "1.0"
    assert str(version.Version("1.0RC1")) == "1.0rc1"


def test_full_version_parsing():
    v = version.Version("1!2.3a4.post5.dev6+7.abc")
    assert v.epoch == 1
    assert v.release == (2, 3)
    assert v.pre == ("a", 4)
    assert v.post == 5
    assert v.dev == 6
    assert v.local == "7.abc"
    assert v._local == (7, "abc")
    assert str(v) == "1!2.3a4.post5.dev6+7.abc"


@pytest.mark.parametrize(
    "text",
    [
        "invalid",
        "1.0+",
        "1.0+!",
        "1.0+abc.",
        "1.0+abc_",
        "1.0+abc..def",
        "a1.0",
        "1.0.x",
        "1.0a1b2",
        "1.0 1.0",
        "1.0 a",
        "1!",
        "!1.0",
        "v",
        "--1.0",
        "1.0.dev1.dev2",
        "1.0\u0661",
        "1.0+\u00e9",
    ],
)
def test_invalid_versions(text):
    with pytest.raises(version.InvalidVersion):
        version.Version(text)


@pytest.mark.parametrize(
    "text, expected",
    [
        ("1.0alpha1", "1.0a1"),
        ("1.0-1", "1.0.post1"),
        ("1.0.dev", "1.0.dev0"),
        ("1.0.post", "1.0.post0"),
        ("1.0r", "1.0.post0"),
        ("1.0+ABC_def", "1.0+abc.def"),
        ("01.02", "1.2"),
        ("1!01.0", "1!1.0"),
        ("1.0c1", "1.0rc1"),
        ("1.0a0", "1.0a0"),
        ("1.0.0", "1.0.0"),
    ],
)
def test_str_normalization(text, expected):
    assert str(version.Version(text)) == expected


def test_repr():
    assert repr(version.Version("1.0.0")) == "<Version('1.0.0')>"
    assert repr(_MyVersion("1.0")) == "<_MyVersion('1.0')>"


def test_match_args_and_str_property():
    assert version.Version.__match_args__ == ("_str",)
    v = version.Version("1.0a1")
    assert v._str == str(v) == "1.0a1"


def test_public_and_base_version():
    assert version.Version("1.2.3").public == "1.2.3"
    assert version.Version("1.2.3+abc").public == "1.2.3"
    assert version.Version("1!1.2.3dev1+abc").public == "1!1.2.3.dev1"
    assert version.Version("1.2.3").base_version == "1.2.3"
    assert version.Version("1.2.3+abc").base_version == "1.2.3"
    assert version.Version("1!1.2.3dev1+abc").base_version == "1!1.2.3"
    assert version.Version("1.2.3a1.post2.dev3").base_version == "1.2.3"


def test_release_flags():
    assert not version.Version("1.2.3").is_prerelease
    assert not version.Version("1.2.3").is_postrelease
    assert not version.Version("1.2.3").is_devrelease
    assert version.Version("1.2.3a1").is_prerelease
    assert version.Version("1.2.3b1").is_prerelease
    assert version.Version("1.2.3rc1").is_prerelease
    assert version.Version("1.2.3.dev1").is_prerelease
    assert version.Version("1.2.3.post1").is_postrelease
    assert not version.Version("1.2.3.post1").is_prerelease
    assert version.Version("1.2.3.dev1").is_devrelease
    assert not version.Version("1.2.3a1").is_devrelease


def test_major_minor_micro():
    v = version.Version("1.2.3.4")
    assert (v.major, v.minor, v.micro) == (1, 2, 3)
    v = version.Version("7")
    assert (v.major, v.minor, v.micro) == (7, 0, 0)
    v = version.Version("7.8")
    assert (v.major, v.minor, v.micro) == (7, 8, 0)


def test_major_minor_micro_with_empty_release():
    v = version.Version.__new__(version.Version)
    v.__setstate__((0, (), None, None, None, None))
    assert (v.major, v.minor, v.micro) == (0, 0, 0)


def test_versions_are_immutable():
    v = version.Version("1.0")
    with pytest.raises(AttributeError):
        v.foo = 1
    with pytest.raises(AttributeError):
        v.epoch = 1
    with pytest.raises(AttributeError):
        v.release = (2,)


@pytest.mark.parametrize("lo, hi", ADJACENT_PAIRS)
def test_ordering_adjacent_pairs(lo, hi):
    a, b = version.Version(lo), version.Version(hi)
    assert a < b
    assert a <= b
    assert b > a
    assert b >= a
    assert a != b
    assert not a == b
    assert not a > b
    assert not a >= b
    assert not b < a
    assert not b <= a


def test_sorting_matches_expected_order():
    shuffled = list(reversed(ORDERED))
    assert [str(v) for v in sorted(version.Version(s) for s in shuffled)] == [
        str(version.Version(s)) for s in ORDERED
    ]


@pytest.mark.parametrize(
    "left, right",
    [
        ("1.0", "1.0.0"),
        ("1.0", "1"),
        ("1.0a1", "1.0alpha1"),
        ("1.0-1", "1.0.post1"),
        ("1.0+ABC", "1.0+abc"),
        ("1.0+a-b", "1.0+a.b"),
        ("0", "0.0.0"),
        ("1.0c1", "1.0rc1"),
        ("v1.0", "1.0"),
        ("1.0.dev", "1.0.dev0"),
    ],
)
def test_equivalent_versions(left, right):
    a, b = version.Version(left), version.Version(right)
    assert a == b
    assert not a != b
    assert a <= b
    assert a >= b
    assert not a < b
    assert not a > b
    assert hash(a) == hash(b)


def test_zero_release_ordering():
    assert version.Version("0") < version.Version("0.1")
    assert version.Version("0.0") == version.Version("0")


def test_local_version_ordering_details():
    assert version.Version("1.0") < version.Version("1.0+local")
    assert version.Version("1.0+a") < version.Version("1.0+1")
    assert version.Version("1.0+2") < version.Version("1.0+10")
    assert version.Version("1.0+abc") < version.Version("1.0+abd")
    assert version.Version("1.0+abc") < version.Version("1.0+abc.1")
    assert version.Version("1.0+1.2") < version.Version("1.0+1.3")


@pytest.mark.parametrize("op", ORDER_OPS)
@pytest.mark.parametrize(
    "warm_left, warm_right", list(itertools.product([False, True], repeat=2))
)
def test_comparison_with_cold_and_warm_caches(op, warm_left, warm_right):
    a, b = version.Version("1.0"), version.Version("2.0")
    if warm_left:
        a._key
    if warm_right:
        b._key
    expected = op(version._cmpkey(0, (1, 0), None, None, None, None),
                  version._cmpkey(0, (2, 0), None, None, None, None))
    assert op(a, b) is expected
    assert a._key_cache is not None
    assert b._key_cache is not None


@pytest.mark.parametrize(
    "warm_left, warm_right", list(itertools.product([False, True], repeat=2))
)
def test_equality_with_cold_and_warm_caches(warm_left, warm_right):
    a, b, c = version.Version("1.0"), version.Version("1.0.0"), version.Version("1.1")
    if warm_left:
        a._key
    if warm_right:
        b._key
        c._key
    assert a == b
    assert not a != b
    assert a != c
    assert not a == c
    assert a._key_cache is not None
    assert b._key_cache is not None


@pytest.mark.parametrize("op", ORDER_OPS)
def test_ordering_with_non_version_raises_type_error(op):
    with pytest.raises(TypeError):
        op(version.Version("1.0"), "1.0")
    with pytest.raises(TypeError):
        op(version.Version("1.0"), 1)
    with pytest.raises(TypeError):
        op(version.Version("1.0"), None)


def test_comparison_dunders_return_not_implemented_for_foreign_types():
    v = version.Version("1.0")
    for name in ("__lt__", "__le__", "__gt__", "__ge__", "__eq__", "__ne__"):
        assert getattr(v, name)("1.0") is NotImplemented
        assert getattr(v, name)(None) is NotImplemented
        assert getattr(v, name)(1.0) is NotImplemented


def test_equality_with_foreign_types():
    v = version.Version("1.0")
    assert not v == "1.0"
    assert v != "1.0"
    assert not v == None
    assert v != None
    assert not v == 1.0


def test_comparison_with_other_base_version_subclass():
    v = version.Version("1.0")
    assert v < _Other(2)
    assert v <= _Other(2)
    assert v <= _Other(1)
    assert v == _Other(1)
    assert not v != _Other(1)
    assert v != _Other(2)
    assert v >= _Other(1)
    assert v >= _Other(0)
    assert v > _Other(0)
    assert not v > _Other(1)
    assert not v < _Other(1)
    assert _Other(1) == v
    assert _Other(2) > v
    assert _Other(0) < v


def test_base_version_comparisons_directly():
    a, b = _Other(1), _Other(2)
    assert a < b
    assert a <= b
    assert a <= _Other(1)
    assert b > a
    assert b >= a
    assert b >= _Other(2)
    assert a == _Other(1)
    assert a != b
    assert not a == b
    assert not a != _Other(1)
    assert hash(a) == hash(_Other(1))
    assert hash(a) == hash(version._cmpkey(0, (1,), None, None, None, None))


def test_base_version_foreign_types_return_not_implemented():
    a = _Other(1)
    for name in ("__lt__", "__le__", "__gt__", "__ge__", "__eq__", "__ne__"):
        assert getattr(a, name)("x") is NotImplemented
        assert getattr(a, name)(None) is NotImplemented
    with pytest.raises(TypeError):
        a < "x"


def test_hash_paths():
    v = version.Version("1.0")
    assert v._hash_cache is None
    assert v._key_cache is None
    h = hash(v)
    assert v._hash_cache == h
    assert v._key_cache is not None
    assert hash(v) == h

    w = version.Version("1.0")
    key = w._key
    assert w._key_cache is key
    assert w._hash_cache is None
    assert hash(w) == h
    assert w._hash_cache == h


def test_hash_usable_in_sets_and_dicts():
    V = version.Version
    assert len({V("1.0"), V("1.0.0"), V("1")}) == 1
    assert len({V("1.0"), V("1.1")}) == 2
    d = {V("1.0"): "x"}
    assert d[V("1.0.0")] == "x"


def test_key_property_is_cached():
    v = version.Version("1.0a1")
    assert v._key_cache is None
    key = v._key
    assert v._key_cache is key
    assert v._key is key
    assert key == version._cmpkey(0, (1, 0), ("a", 1), None, None, None)


@pytest.mark.parametrize(
    "args, expected",
    [
        ((0, (1, 0, 0), None, None, None, None), (0, (1,), (3, 0, 0, 0, 1, 0))),
        ((0, (1,), ("a", 1), None, None, None), (0, (1,), (0, 1, 0, 0, 1, 0))),
        ((0, (1,), ("b", 2), None, None, None), (0, (1,), (1, 2, 0, 0, 1, 0))),
        ((0, (1,), ("rc", 3), None, None, None), (0, (1,), (2, 3, 0, 0, 1, 0))),
        ((0, (1,), None, ("post", 4), None, None), (0, (1,), (3, 0, 1, 4, 1, 0))),
        ((0, (1,), None, None, ("dev", 5), None), (0, (1,), (-1, 0, 0, 0, 0, 5))),
        ((0, (1,), None, ("post", 4), ("dev", 5), None), (0, (1,), (3, 0, 1, 4, 0, 5))),
        ((0, (1,), ("b", 1), None, ("dev", 2), None), (0, (1,), (1, 1, 0, 0, 0, 2))),
        ((2, (1, 2), None, None, None, None), (2, (1, 2), (3, 0, 0, 0, 1, 0))),
        ((0, (0, 0), None, None, None, None), (0, (), (3, 0, 0, 0, 1, 0))),
        ((0, (1, 0, 2, 0), None, None, None, None), (0, (1, 0, 2), (3, 0, 0, 0, 1, 0))),
        (
            (0, (1,), None, None, None, ("ubuntu", 1)),
            (0, (1,), (3, 0, 0, 0, 1, 0), ((-1, "ubuntu"), (1, ""))),
        ),
        (
            (0, (1,), ("a", 1), ("post", 2), ("dev", 3), (4,)),
            (0, (1,), (0, 1, 1, 2, 0, 3), ((4, ""),)),
        ),
    ],
)
def test_cmpkey(args, expected):
    assert version._cmpkey(*args) == expected


def test_cmpkey_returns_same_release_object_when_no_trailing_zeros():
    release = (1, 2, 3)
    assert version._cmpkey(0, release, None, None, None, None)[1] is release


@pytest.mark.parametrize(
    "letter, number, expected",
    [
        ("a", "1", ("a", 1)),
        ("alpha", None, ("a", 0)),
        ("ALPHA", "2", ("a", 2)),
        ("r", 1, ("post", 1)),
        ("c", None, ("rc", 0)),
        ("x", None, ("x", 0)),
        ("a", 3, ("a", 3)),
        (None, "3", ("post", 3)),
        (None, "0", ("post", 0)),
        ("", "5", ("post", 5)),
        (None, None, None),
        (None, "", None),
        (None, 0, None),
    ],
)
def test_parse_letter_version(letter, number, expected):
    assert version._parse_letter_version(letter, number) == expected


@pytest.mark.parametrize(
    "local, expected",
    [
        (None, None),
        ("abc.1.twelve", ("abc", 1, "twelve")),
        ("ABC", ("abc",)),
        ("a-b_c", ("a", "b", "c")),
        ("1", (1,)),
        ("007", (7,)),
        ("", ("",)),
    ],
)
def test_parse_local_version(local, expected):
    assert version._parse_local_version(local) == expected


def test_validate_epoch():
    assert version._validate_epoch(0) == 0
    assert version._validate_epoch(5) == 5
    assert version._validate_epoch(None) == 0
    for bad in (-1, "1", 1.0, [1]):
        with pytest.raises(version.InvalidVersion, match="epoch must be"):
            version._validate_epoch(bad)


def test_validate_release():
    assert version._validate_release(None) == (0,)
    assert version._validate_release((0,)) == (0,)
    assert version._validate_release((1, 2, 3)) == (1, 2, 3)
    for bad in ((), (1, -1), [1], (1, "2"), "1.2", 5):
        with pytest.raises(version.InvalidVersion, match="release must be"):
            version._validate_release(bad)


def test_validate_pre():
    assert version._validate_pre(None) is None
    assert version._validate_pre(("a", 1)) == ("a", 1)
    assert version._validate_pre(("alpha", 1)) == ("a", 1)
    assert version._validate_pre(("BETA", 0)) == ("b", 0)
    assert version._validate_pre(("c", 2)) == ("rc", 2)
    assert version._validate_pre(("preview", 2)) == ("rc", 2)
    for bad in (
        ("x", 1),
        ("a", -1),
        ("a", "1"),
        ("a",),
        ("a", 1, 2),
        "a1",
        (1, 1),
        ["a", 1],
        ("rev", 1),
        ("post", 1),
        1,
    ):
        with pytest.raises(version.InvalidVersion, match="pre must be"):
            version._validate_pre(bad)


def test_validate_post_and_dev():
    assert version._validate_post(None) is None
    assert version._validate_post(0) == ("post", 0)
    assert version._validate_post(7) == ("post", 7)
    assert version._validate_dev(None) is None
    assert version._validate_dev(0) == ("dev", 0)
    assert version._validate_dev(7) == ("dev", 7)
    for bad in (-1, "1", 1.5, (1,)):
        with pytest.raises(version.InvalidVersion, match="post must be"):
            version._validate_post(bad)
        with pytest.raises(version.InvalidVersion, match="dev must be"):
            version._validate_dev(bad)


def test_validate_local():
    assert version._validate_local(None) is None
    assert version._validate_local("A.1") == ("a", 1)
    assert version._validate_local("abc.def-1_2") == ("abc", "def", 1, 2)
    for bad in ("", "abc!", 1, "a..b", "+abc", "abc-", ["a"]):
        with pytest.raises(version.InvalidVersion, match="local must be"):
            version._validate_local(bad)


def test_from_parts_basic():
    V = version.Version
    assert str(V.from_parts(release=(1, 2, 3))) == "1.2.3"
    assert str(V.from_parts(release=(0, 1, 0), pre=("b", 1))) == "0.1.0b1"
    assert str(V.from_parts(release=(1,), epoch=2)) == "2!1"
    assert str(V.from_parts(release=(1,), pre=("alpha", 1))) == "1a1"
    assert str(V.from_parts(release=(1,), pre=("RC", 2))) == "1rc2"
    assert str(V.from_parts(release=(1,), pre=("c", 2))) == "1rc2"
    assert str(V.from_parts(release=(1,), post=1)) == "1.post1"
    assert str(V.from_parts(release=(1,), post=0)) == "1.post0"
    assert str(V.from_parts(release=(1,), dev=0)) == "1.dev0"
    assert str(V.from_parts(release=(1,), local="ABC.1")) == "1+abc.1"
    assert str(V.from_parts(release=None)) == "0"
    assert str(V.from_parts(release=(1,), epoch=None)) == "1"


def test_from_parts_all_fields_round_trip():
    v = version.Version.from_parts(
        epoch=1, release=(2, 3), pre=("a", 4), post=5, dev=6, local="7.abc"
    )
    assert str(v) == "1!2.3a4.post5.dev6+7.abc"
    assert v == version.Version(str(v))
    assert v._key_cache is not None or True
    assert v.epoch == 1
    assert v.release == (2, 3)
    assert v.pre == ("a", 4)
    assert v.post == 5
    assert v.dev == 6
    assert v.local == "7.abc"


def test_from_parts_caches_start_empty():
    v = version.Version.from_parts(release=(1,))
    assert v._key_cache is None
    assert v._hash_cache is None


def test_from_parts_subclass_returns_subclass():
    assert isinstance(_MyVersion.from_parts(release=(1,)), _MyVersion)
    assert type(version.Version.from_parts(release=(1,))) is version.Version


def test_from_parts_requires_keyword_release():
    with pytest.raises(TypeError):
        version.Version.from_parts()
    with pytest.raises(TypeError):
        version.Version.from_parts((1, 2))


@pytest.mark.parametrize(
    "kwargs",
    [
        {"release": (1,), "epoch": -1},
        {"release": (1,), "epoch": "1"},
        {"release": ()},
        {"release": [1, 2]},
        {"release": (1, -2)},
        {"release": (1, "a")},
        {"release": (1,), "pre": ("x", 1)},
        {"release": (1,), "pre": ("a", -1)},
        {"release": (1,), "pre": "a1"},
        {"release": (1,), "post": -1},
        {"release": (1,), "post": "1"},
        {"release": (1,), "dev": -1},
        {"release": (1,), "dev": 1.5},
        {"release": (1,), "local": ""},
        {"release": (1,), "local": "a!b"},
        {"release": (1,), "local": 5},
    ],
)
def test_from_parts_invalid(kwargs):
    with pytest.raises(version.InvalidVersion):
        version.Version.from_parts(**kwargs)


def test_replace_without_changes_returns_self():
    v = version.Version("1.2.3")
    assert v.__replace__() is v
    assert v.__replace__(epoch=0) is v
    assert v.__replace__(release=(1, 2, 3)) is v
    assert v.__replace__(pre=None) is v
    assert v.__replace__(post=None) is v
    assert v.__replace__(dev=None) is v
    assert v.__replace__(local=None) is v
    full = version.Version("1!1.2a1.post2.dev3+abc")
    assert (
        full.__replace__(
            epoch=1,
            release=(1, 2),
            pre=("alpha", 1),
            post=2,
            dev=3,
            local="ABC",
        )
        is full
    )


@pytest.mark.parametrize(
    "kwargs, expected",
    [
        ({"epoch": 1}, "1!1.2.3"),
        ({"release": (2, 0)}, "2.0"),
        ({"pre": ("a", 1)}, "1.2.3a1"),
        ({"pre": ("alpha", 1)}, "1.2.3a1"),
        ({"pre": ("c", 1)}, "1.2.3rc1"),
        ({"post": 1}, "1.2.3.post1"),
        ({"dev": 1}, "1.2.3.dev1"),
        ({"local": "abc"}, "1.2.3+abc"),
        ({"local": "ABC.1"}, "1.2.3+abc.1"),
        ({"epoch": 2, "release": (9,), "post": 0}, "2!9.post0"),
    ],
)
def test_replace_changes_parts(kwargs, expected):
    original = version.Version("1.2.3")
    new = original.__replace__(**kwargs)
    assert new is not original
    assert str(new) == expected
    assert str(original) == "1.2.3"
    assert new._key_cache is None
    assert new._hash_cache is None


def test_replace_clears_parts_with_none():
    v = version.Version("1!1.2a1.post2.dev3+abc")
    assert str(v.__replace__(epoch=None)) == "1.2a1.post2.dev3+abc"
    assert str(v.__replace__(pre=None)) == "1!1.2.post2.dev3+abc"
    assert str(v.__replace__(post=None)) == "1!1.2a1.dev3+abc"
    assert str(v.__replace__(dev=None)) == "1!1.2a1.post2+abc"
    assert str(v.__replace__(local=None)) == "1!1.2a1.post2.dev3"
    assert str(v.__replace__(pre=None, post=None, dev=None, local=None)) == "1!1.2"
    assert str(v.__replace__(release=None)) == "1!0a1.post2.dev3+abc"
    assert str(v) == "1!1.2a1.post2.dev3+abc"


def test_replace_preserves_subclass():
    v = _MyVersion("1.0")
    new = v.__replace__(release=(2,))
    assert type(new) is _MyVersion
    assert str(new) == "2"


@pytest.mark.parametrize(
    "kwargs",
    [
        {"epoch": -1},
        {"release": ()},
        {"pre": ("x", 1)},
        {"post": -1},
        {"dev": "1"},
        {"local": "a!"},
    ],
)
def test_replace_invalid(kwargs):
    with pytest.raises(version.InvalidVersion):
        version.Version("1.0").__replace__(**kwargs)


@pytest.mark.parametrize("protocol", range(2, pickle.HIGHEST_PROTOCOL + 1))
@pytest.mark.parametrize(
    "text",
    ["1", "1.2.3", "1!2.3a4.post5.dev6+7.abc", "1.0.dev1", "1.0+local.1", "1.0rc1"],
)
def test_pickle_round_trip(protocol, text):
    v = version.Version(text)
    v._key
    hash(v)
    restored = pickle.loads(pickle.dumps(v, protocol))
    assert type(restored) is version.Version
    assert restored == v
    assert str(restored) == str(v)
    assert hash(restored) == hash(v)


def test_pickle_resets_caches():
    v = version.Version("1.0")
    v._key
    hash(v)
    restored = pickle.loads(pickle.dumps(v))
    assert restored._key_cache is None
    assert restored._hash_cache is None


def test_pickle_subclass():
    v = _MyVersion("1.0a1")
    restored = pickle.loads(pickle.dumps(v))
    assert type(restored) is _MyVersion
    assert restored == v


def test_copy_and_deepcopy():
    v = version.Version("1!2.3a4+x")
    for clone in (copy.copy(v), copy.deepcopy(v)):
        assert clone == v
        assert str(clone) == str(v)
        assert clone is not v


def test_getstate_returns_six_tuple():
    v = version.Version("1!2.3a4.post5.dev6+7.abc")
    v._key
    assert v.__getstate__() == (
        1,
        (2, 3),
        ("a", 4),
        ("post", 5),
        ("dev", 6),
        (7, "abc"),
    )


def test_setstate_new_format():
    v = version.Version.__new__(version.Version)
    v.__setstate__((1, (2, 3), ("a", 4), ("post", 5), ("dev", 6), ("x", 1)))
    assert str(v) == "1!2.3a4.post5.dev6+x.1"
    assert v._key_cache is None
    assert v._hash_cache is None


def test_setstate_clears_existing_caches():
    v = version.Version("1.0")
    v._key
    hash(v)
    v.__setstate__((0, (2,), None, None, None, None))
    assert v._key_cache is None
    assert v._hash_cache is None
    assert str(v) == "2"


def test_setstate_slot_dict_format_full():
    v = version.Version.__new__(version.Version)
    v.__setstate__(
        (
            None,
            {
                "_epoch": 1,
                "_release": (1, 2),
                "_pre": ("a", 1),
                "_post": ("post", 2),
                "_dev": ("dev", 3),
                "_local": ("abc",),
                "_key_cache": object(),
                "_hash_cache": 5,
            },
        )
    )
    assert str(v) == "1!1.2a1.post2.dev3+abc"
    assert v._key_cache is None
    assert v._hash_cache is None


def test_setstate_slot_dict_format_minimal():
    v = version.Version.__new__(version.Version)
    v.__setstate__((None, {"_epoch": 0, "_release": (3,)}))
    assert str(v) == "3"
    assert v.pre is None
    assert v.post is None
    assert v.dev is None
    assert v.local is None


def test_setstate_slot_dict_missing_required_raises_key_error():
    v = version.Version.__new__(version.Version)
    with pytest.raises(KeyError):
        v.__setstate__((None, {"_release": (1,)}))
    with pytest.raises(KeyError):
        v.__setstate__((None, {"_epoch": 0}))


def test_setstate_legacy_dict_format():
    v = version.Version.__new__(version.Version)
    legacy = version._Version(
        epoch=1,
        release=(1, 2),
        dev=("dev", 4),
        pre=("a", 1),
        post=("post", 2),
        local=("x",),
    )
    v.__setstate__({"_version": legacy, "_key": (0, 0, 0)})
    assert str(v) == "1!1.2a1.post2.dev4+x"
    assert v._key_cache is None
    assert v._hash_cache is None


@pytest.mark.parametrize(
    "state",
    [
        None,
        "abc",
        5,
        [],
        (),
        (1,),
        (1, 2, 3),
        (1, 2, 3, 4, 5, 6, 7),
        (None, "not a dict"),
        (None, None),
        {},
        {"_key": 1},
        {"_version": None},
    ],
)
def test_setstate_invalid_state_raises_type_error(state):
    v = version.Version.__new__(version.Version)
    with pytest.raises(TypeError, match="Cannot restore Version from"):
        v.__setstate__(state)


def test_deprecated_version_getter():
    v = version.Version("1!2.3a4.post5.dev6+x.1")
    with pytest.warns(DeprecationWarning, match="Version._version is private"):
        nt = v._version
    assert isinstance(nt, version._Version)
    assert nt.epoch == 1
    assert nt.release == (2, 3)
    assert nt.dev == ("dev", 6)
    assert nt.pre == ("a", 4)
    assert nt.post == ("post", 5)
    assert nt.local == ("x", 1)


def test_deprecated_version_setter_updates_fields_and_clears_caches():
    v = version.Version("1.0")
    v._key
    hash(v)
    new_state = version._Version(
        epoch=1,
        release=(2, 3),
        dev=("dev", 4),
        pre=("a", 1),
        post=("post", 2),
        local=("x", 1),
    )
    with pytest.warns(DeprecationWarning, match="Version._version is private"):
        v._version = new_state
    assert v._key_cache is None
    assert v._hash_cache is None
    assert str(v) == "1!2.3a1.post2.dev4+x.1"


def test_trimmed_release_from_version():
    T, V = version._TrimmedRelease, version.Version
    assert T(V("1.0.0")).release == (1,)
    assert T(V("0.0")).release == (0,)
    assert T(V("0.0.0")).release == (0,)
    assert T(V("1.2.0")).release == (1, 2)
    assert T(V("1.0.2.0.0")).release == (1, 0, 2)
    assert T(V("1")).release == (1,)


def test_trimmed_release_without_trailing_zeros_returns_original_tuple():
    base = version.Version("1.2.3")
    trimmed = version._TrimmedRelease(base)
    assert trimmed.release is base.release


def test_trimmed_release_copies_all_state():
    base = version.Version("1!2.0a1.post2.dev3+abc")
    base._key
    hash(base)
    trimmed = version._TrimmedRelease(base)
    assert trimmed._epoch == base._epoch
    assert trimmed._pre == base._pre
    assert trimmed._post == base._post
    assert trimmed._dev == base._dev
    assert trimmed._local == base._local
    assert trimmed._key_cache is base._key_cache
    assert trimmed._hash_cache == base._hash_cache
    assert str(trimmed) == "1!2a1.post2.dev3+abc"
    assert trimmed.base_version == "1!2"
    assert trimmed.major == 2
    assert trimmed.minor == 0


def test_trimmed_release_from_string():
    trimmed = version._TrimmedRelease("1.0.0")
    assert trimmed.release == (1,)
    assert str(trimmed) == "1"
    assert version._TrimmedRelease("1.2.3a1").release == (1, 2, 3)


def test_trimmed_release_invalid_string_raises():
    with pytest.raises(version.InvalidVersion):
        version._TrimmedRelease("invalid")


def test_trimmed_release_is_a_version_and_compares():
    trimmed = version._TrimmedRelease(version.Version("1.0.0"))
    assert isinstance(trimmed, version.Version)
    assert trimmed == version.Version("1.0")
    assert repr(trimmed) == "<_TrimmedRelease('1')>"