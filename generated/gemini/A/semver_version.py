import pytest
from semver.version import Version


def test_version_initialization():
    v = Version(1, 2, 3, "rc.1", "build.1")
    assert v.major == 1
    assert v.minor == 2
    assert v.patch == 3
    assert v.prerelease == "rc.1"
    assert v.build == "build.1"


def test_version_negative_value():
    with pytest.raises(ValueError):
        Version(-1, 0, 0)
    with pytest.raises(ValueError):
        Version(1, -1, 0)
    with pytest.raises(ValueError):
        Version(1, 0, -1)


def test_readonly_attributes():
    v = Version(1, 0, 0)
    with pytest.raises(AttributeError):
        v.major = 2
    with pytest.raises(AttributeError):
        v.minor = 2
    with pytest.raises(AttributeError):
        v.patch = 2
    with pytest.raises(AttributeError):
        v.prerelease = "rc.2"
    with pytest.raises(AttributeError):
        v.build = "build.2"


def test_to_tuple_and_dict():
    v = Version(1, 2, 3, "rc.1", "meta")
    assert v.to_tuple() == (1, 2, 3, "rc.1", "meta")
    assert v.to_dict() == {
        "major": 1,
        "minor": 2,
        "patch": 3,
        "prerelease": "rc.1",
        "build": "meta",
    }
    assert list(v) == [1, 2, 3, "rc.1", "meta"]


def test_bump_methods():
    v = Version(1, 2, 3, "rc.1", "build.1")
    assert v.bump_major() == Version(2, 0, 0)
    assert v.bump_minor() == Version(1, 3, 0)
    assert v.bump_patch() == Version(1, 2, 4)
    assert v.bump_prerelease().prerelease == "rc.2"
    assert v.bump_prerelease("alpha").prerelease == "alpha.1"
    assert v.bump_prerelease("").prerelease == "1"
    assert v.bump_prerelease(None).prerelease == "rc.1"

    v_clean = Version(1, 2, 3)
    assert v_clean.bump_prerelease(bump_when_empty=True) == Version(1, 2, 4, "rc.1")

    v_build = Version(1, 2, 3, build="abc")
    assert v_build.bump_build() == Version(1, 2, 3, prerelease=None, build="abc.1")
    assert Version(1, 2, 3).bump_build(None) == Version(1, 2, 3, build="build.1")
    assert Version(1, 2, 3).bump_build("") == Version(1, 2, 3, build="0")


def test_compare():
    v1 = Version(1, 0, 0)
    v2 = Version(2, 0, 0)
    assert v1.compare(v2) == -1
    assert v2.compare(v1) == 1
    assert v1.compare(v1) == 0
    assert v1.compare("2.0.0") == -1
    assert v1.compare({"major": 1, "minor": 0, "patch": 0}) == 0
    assert v1.compare((1, 0, 0)) == 0

    with pytest.raises(TypeError):
        v1.compare(123)

    v_pre1 = Version.parse("1.0.0-rc.1")
    v_pre2 = Version.parse("1.0.0-rc.2")
    v_main = Version.parse("1.0.0")
    assert v_pre1.compare(v_pre2) == -1
    assert v_main.compare(v_pre1) == 1
    assert v_pre1.compare(v_main) == -1


def test_comparators():
    v1 = Version(1, 0, 0)
    v2 = Version(2, 0, 0)
    assert (v1 < v2) is True
    assert (v1 <= v2) is True
    assert (v1 > v2) is False
    assert (v1 >= v2) is False
    assert (v1 == v2) is False
    assert (v1 != v2) is True
    assert (v1 == "1.0.0") is True
    assert (v1 == {"major": 2}) is False
    assert (v1 == 123) is NotImplemented


def test_getitem():
    v = Version(1, 2, 3, "rc.1", "build.1")
    assert v[0] == 1
    assert v[1] == 2
    assert v[2] == 3
    assert v[3] == "rc.1"
    assert v[4] == "build.1"
    assert v[0:3] == (1, 2, 3)

    with pytest.raises(IndexError):
        _ = v[-1]

    v_no_pre = Version(1, 2, 3)
    with pytest.raises(IndexError):
        _ = v_no_pre[3]


def test_repr_str_hash():
    v = Version(1, 2, 3, "rc.1", "build.1")
    assert str(v) == "1.2.3-rc.1+build.1"
    assert repr(v) == "Version(major=1, minor=2, patch=3, prerelease='rc.1', build='build.1')"
    assert hash(v) == hash((1, 2, 3, "rc.1"))


def test_finalize_version():
    v = Version(1, 2, 3, "rc.1", "build.1")
    assert v.finalize_version() == Version(1, 2, 3)


def test_match():
    v = Version(2, 0, 0)
    assert v.match(">=1.0.0") is True
    assert v.match(">2.0.0") is False
    assert v.match("2.0.0") is True
    assert v.match("!=1.0.0") is True
    assert v.match("<=2.0.0") is True
    assert v.match("<2.0.0") is False

    with pytest.raises(ValueError):
        v.match("invalid_expr")


def test_parse():
    v = Version.parse("1.2.3-rc.1+build.1")
    assert v == Version(1, 2, 3, "rc.1", "build.1")
    assert Version.parse(b"1.2.3") == Version(1, 2, 3)

    with pytest.raises(TypeError):
        Version.parse(123)  # type: ignore

    with pytest.raises(ValueError):
        Version.parse("invalid_version")

    v_opt = Version.parse("1.2", optional_minor_and_patch=True)
    assert v_opt == Version(1, 2, 0)
    v_opt2 = Version.parse("1", optional_minor_and_patch=True)
    assert v_opt2 == Version(1, 0, 0)

    with pytest.raises(ValueError):
        Version.parse("1.a", optional_minor_and_patch=True)


def test_replace():
    v = Version(1, 2, 3)
    v2 = v.replace(major=2, prerelease="rc.1")
    assert v2 == Version(2, 2, 3, "rc.1")

    with pytest.raises(TypeError):
        v.replace(unknown_key=5)


def test_is_valid():
    assert Version.is_valid("1.2.3") is True
    assert Version.is_valid("invalid") is False


def test_is_compatible():
    v1 = Version(1, 1, 0)
    v2 = Version(1, 0, 0)
    assert v1.is_compatible(v2) is False
    assert v2.is_compatible(v1) is True

    v0_1 = Version(0, 1, 0)
    v0_2 = Version(0, 2, 0)
    assert v0_1.is_compatible(v0_2) is False
    assert v0_1.is_compatible(v0_1) is True

    with pytest.raises(TypeError):
        v1.is_compatible("1.1.0")  # type: ignore


def test_next_version():
    v = Version(1, 2, 3)
    assert v.next_version("major") == Version(2, 0, 0)
    assert v.next_version("minor") == Version(1, 3, 0)
    assert v.next_version("patch") == Version(1, 2, 4)
    assert v.next_version("prerelease") == Version(1, 2, 4, "rc.1")

    v_pre = Version.parse("0.1.4")
    assert v_pre.next_version("prerelease") == Version(0, 1, 5, "rc.1")

    v_rc = Version.parse("1.2.3-rc.1")
    assert v_rc.next_version("prerelease", "alpha") == Version(1, 2, 4, "alpha.1")

    v_old_rc = Version.parse("1.2.3-rc9")
    assert v_old_rc.next_version("prerelease") == Version(1, 2, 4, "rc10")

    with pytest.raises(ValueError):
        v.next_version("invalid_part")


def test_nat_cmp_edge_cases():
    assert Version._nat_cmp("01", "1") == 0
    assert Version._nat_cmp("a", "1") == 1
    assert Version._nat_cmp("1", "a") == -1