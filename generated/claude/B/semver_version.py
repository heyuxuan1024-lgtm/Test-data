import pytest

from semver import version


class SubVersion(version.Version):
    pass


class IndexLike:
    def __init__(self, value):
        self.value = value

    def __index__(self):
        return self.value


@pytest.fixture(autouse=True)
def no_native_backend(monkeypatch):
    monkeypatch.setattr(version, "_native_parse_parts", None)


def test_version_info_alias():
    assert version.VersionInfo is version.Version


def test_names_and_slots():
    assert version.Version.NAMES == ("major", "minor", "patch", "prerelease", "build")
    assert version.Version.__slots__ == (
        "_major",
        "_minor",
        "_patch",
        "_prerelease",
        "_build",
    )


@pytest.mark.parametrize(
    "a, b, expected",
    [
        (1, 2, -1),
        (2, 1, 1),
        (1, 1, 0),
        ("a", "b", -1),
        ("b", "a", 1),
        ((1, 2), (1, 3), -1),
        ((1, 3), (1, 2), 1),
        ((1, 2), (1, 2), 0),
    ],
)
def test_cmp(a, b, expected):
    assert version._cmp(a, b) == expected


def test_init_defaults():
    assert version.Version(1).to_tuple() == (1, 0, 0, None, None)


def test_init_all_parts():
    v = version.Version(1, 2, 3, "rc.1", "b.5")
    assert v.to_tuple() == (1, 2, 3, "rc.1", "b.5")


def test_init_coerces_numeric_types():
    v = version.Version("1", "2", "3")
    assert v.to_tuple()[:3] == (1, 2, 3)
    assert version.Version(1.9).major == 1


def test_init_stringifies_prerelease_and_build():
    v = version.Version(1, 0, 0, prerelease=5, build=7)
    assert v.prerelease == "5"
    assert v.build == "7"


def test_init_keeps_empty_strings():
    v = version.Version(1, 0, 0, prerelease="", build="")
    assert v.prerelease == ""
    assert v.build == ""


@pytest.mark.parametrize(
    "args, name",
    [((-1,), "major"), ((1, -1), "minor"), ((1, 1, -1), "patch")],
)
def test_init_negative_raises(args, name):
    with pytest.raises(ValueError, match=f"'{name}' is negative"):
        version.Version(*args)


def test_init_invalid_values_raise():
    with pytest.raises(ValueError):
        version.Version("x")
    with pytest.raises(TypeError):
        version.Version(None)
    with pytest.raises(TypeError):
        version.Version()
    with pytest.raises(TypeError):
        version.Version(1, 2, 3, "a", "b", "c")


@pytest.mark.parametrize("name", ["major", "minor", "patch", "prerelease", "build"])
def test_properties_are_read_only(name):
    v = version.Version(1, 2, 3, "rc", "b")
    with pytest.raises(AttributeError, match="readonly"):
        setattr(v, name, 5)


def test_unknown_attribute_cannot_be_set():
    with pytest.raises(AttributeError):
        version.Version(1).foo = 1


def test_to_tuple_and_to_dict():
    v = version.Version(3, 2, 1, "rc", "b")
    assert v.to_tuple() == (3, 2, 1, "rc", "b")
    assert isinstance(v.to_tuple(), tuple)
    assert v.to_dict() == {
        "major": 3,
        "minor": 2,
        "patch": 1,
        "prerelease": "rc",
        "build": "b",
    }
    assert list(v.to_dict()) == ["major", "minor", "patch", "prerelease", "build"]


def test_iter():
    assert list(version.Version(1, 2, 3, "a", "b")) == [1, 2, 3, "a", "b"]
    major, minor, patch, pre, build = version.Version(1, 2, 3)
    assert (major, minor, patch, pre, build) == (1, 2, 3, None, None)


def test_str():
    V = version.Version
    assert str(V(1, 2, 3)) == "1.2.3"
    assert str(V(1, 2, 3, "rc.1")) == "1.2.3-rc.1"
    assert str(V(1, 2, 3, build="b")) == "1.2.3+b"
    assert str(V(1, 2, 3, "rc.1", "b")) == "1.2.3-rc.1+b"
    assert str(V(1, 2, 3, "", "")) == "1.2.3"
    assert str(V(0, 0, 0)) == "0.0.0"


def test_repr():
    V = version.Version
    assert repr(V(1, 2, 3)) == (
        "Version(major=1, minor=2, patch=3, prerelease=None, build=None)"
    )
    assert repr(V(1, 2, 3, "rc.1", "b")) == (
        "Version(major=1, minor=2, patch=3, prerelease='rc.1', build='b')"
    )
    assert repr(SubVersion(1)).startswith("SubVersion(")


def test_hash():
    V = version.Version
    assert hash(V(1, 2, 3)) == hash(V(1, 2, 3))
    assert hash(V(1, 2, 3)) == hash(V(1, 2, 3, build="x"))
    assert {V(1, 2, 3): 1}[V(1, 2, 3, build="x")] == 1
    assert len({V(1, 2, 3), V(1, 2, 3, build="y")}) == 1
    assert len({V(1, 2, 3), V(1, 2, 3, "rc.1")}) == 2


@pytest.mark.parametrize(
    "text, expected",
    [
        ("0.0.0", (0, 0, 0, None, None)),
        ("1.2.3", (1, 2, 3, None, None)),
        ("10.20.30", (10, 20, 30, None, None)),
        ("1.2.3-rc.1", (1, 2, 3, "rc.1", None)),
        ("1.2.3+build.5", (1, 2, 3, None, "build.5")),
        ("1.2.3-rc.1+build.5", (1, 2, 3, "rc.1", "build.5")),
        ("1.2.3-0", (1, 2, 3, "0", None)),
        ("1.2.3-0a", (1, 2, 3, "0a", None)),
        ("1.2.3-x-y.z", (1, 2, 3, "x-y.z", None)),
        ("1.2.3+001", (1, 2, 3, None, "001")),
        ("1.2.3+0-1", (1, 2, 3, None, "0-1")),
        ("1.0.0-0.3.7", (1, 0, 0, "0.3.7", None)),
        ("1.0.0-x-y-z.--", (1, 0, 0, "x-y-z.--", None)),
        ("1.2.3-a.1.b.2+c.3.d", (1, 2, 3, "a.1.b.2", "c.3.d")),
    ],
)
def test_parse_valid(text, expected):
    assert version.Version.parse(text).to_tuple() == expected


@pytest.mark.parametrize(
    "text",
    [
        "",
        "1",
        "1.2",
        "1.2.3.4",
        "01.2.3",
        "1.02.3",
        "1.2.03",
        "-1.2.3",
        "v1.2.3",
        " 1.2.3",
        "1.2.3 ",
        "1.2.3\n",
        "1.2.3-",
        "1.2.3+",
        "1.2.3-+b",
        "1.2.3-01",
        "1.2.3-rc..1",
        "1.2.3-rc.",
        "1.2.3+b..c",
        "1.2.3+b.",
        "1.2.3-a_b",
        "1.2.3+\u00e9",
        "\u0661.\u0662.\u0663",
        "a.b.c",
        "1.2.3-rc.1+b+c",
        "1.2.3-rc 1",
    ],
)
def test_parse_invalid(text):
    with pytest.raises(ValueError, match="is not valid SemVer string"):
        version.Version.parse(text)


def test_parse_bytes():
    assert version.Version.parse(b"1.2.3-rc.1+b") == version.Version(
        1, 2, 3, "rc.1", "b"
    )


def test_parse_invalid_utf8_bytes():
    with pytest.raises(UnicodeDecodeError):
        version.Version.parse(b"\xff")


@pytest.mark.parametrize(
    "bad", [None, 123, 1.5, ["1.2.3"], bytearray(b"1.2.3"), (1, 2, 3)]
)
def test_parse_wrong_type(bad):
    with pytest.raises(TypeError, match="not expecting type"):
        version.Version.parse(bad)


def test_parse_huge_numbers():
    big = 10**30
    assert version.Version.parse(f"{big}.0.0").major == big


@pytest.mark.parametrize(
    "text, expected",
    [
        ("0", (0, 0, 0, None, None)),
        ("1", (1, 0, 0, None, None)),
        ("1.2", (1, 2, 0, None, None)),
        ("1.2.3", (1, 2, 3, None, None)),
        ("1-rc.1", (1, 0, 0, "rc.1", None)),
        ("1.2+b", (1, 2, 0, None, "b")),
        ("1.2-a+b", (1, 2, 0, "a", "b")),
        ("1.2.3-rc.1+b", (1, 2, 3, "rc.1", "b")),
    ],
)
def test_parse_optional_minor_and_patch(text, expected):
    result = version.Version.parse(text, optional_minor_and_patch=True)
    assert result.to_tuple() == expected


@pytest.mark.parametrize(
    "text", ["", "1.", "01", "1.2.", "1.2.3.4", "1..3", "a", "1.02"]
)
def test_parse_optional_minor_and_patch_invalid(text):
    with pytest.raises(ValueError, match="is not valid SemVer string"):
        version.Version.parse(text, optional_minor_and_patch=True)


def test_parse_strict_rejects_short_versions():
    with pytest.raises(ValueError):
        version.Version.parse("1.2")
    with pytest.raises(ValueError):
        version.Version.parse("1")


def test_parse_returns_subclass():
    assert type(SubVersion.parse("1.2.3")) is SubVersion
    assert type(version.Version.parse("1.2.3")) is version.Version


def test_parse_uses_native_backend(monkeypatch):
    calls = []

    def fake(text):
        calls.append(text)
        return (7, 8, 9, "x", None)

    monkeypatch.setattr(version, "_native_parse_parts", fake)
    v = version.Version.parse("1.2.3")
    assert calls == ["1.2.3"]
    assert str(v) == "7.8.9-x"


def test_parse_native_backend_receives_decoded_bytes(monkeypatch):
    calls = []

    def fake(text):
        calls.append(text)
        return (1, 2, 3, None, None)

    monkeypatch.setattr(version, "_native_parse_parts", fake)
    version.Version.parse(b"1.2.3")
    assert calls == ["1.2.3"]


def test_parse_native_backend_value_error_falls_back(monkeypatch):
    def fake(text):
        raise ValueError("too big")

    monkeypatch.setattr(version, "_native_parse_parts", fake)
    assert version.Version.parse("1.2.3") == version.Version(1, 2, 3)
    with pytest.raises(ValueError, match="is not valid SemVer string"):
        version.Version.parse("bad")


def test_parse_native_backend_other_errors_propagate(monkeypatch):
    def fake(text):
        raise RuntimeError("boom")

    monkeypatch.setattr(version, "_native_parse_parts", fake)
    with pytest.raises(RuntimeError):
        version.Version.parse("1.2.3")


def test_parse_native_backend_skipped_for_optional_parts(monkeypatch):
    calls = []

    def fake(text):
        calls.append(text)
        return (9, 9, 9, None, None)

    monkeypatch.setattr(version, "_native_parse_parts", fake)
    result = version.Version.parse("1.2", optional_minor_and_patch=True)
    assert result == version.Version(1, 2, 0)
    assert calls == []


def test_is_valid():
    V = version.Version
    assert V.is_valid("1.2.3")
    assert V.is_valid(b"1.2.3")
    assert V.is_valid("1.2.3-rc.1+b")
    assert not V.is_valid("1.2")
    assert not V.is_valid("1.2.3-")
    assert not V.is_valid("")
    assert not V.is_valid(b"\xff")


def test_is_valid_wrong_type_raises():
    with pytest.raises(TypeError):
        version.Version.is_valid(5)
    with pytest.raises(TypeError):
        version.Version.is_valid(None)


@pytest.mark.parametrize(
    "value", ["0", "1", "10", "a", "a1", "1a", "-", "a-b", "0a", "--1", "Abc", "rc"]
)
def test_prerelease_identifier_valid(value):
    assert version.Version._PRERELEASE_IDENTIFIER.fullmatch(value)


@pytest.mark.parametrize(
    "value", ["", "00", "01", "a_b", "a b", "\u00e9", "\u0663", "a.b"]
)
def test_prerelease_identifier_invalid(value):
    assert not version.Version._PRERELEASE_IDENTIFIER.fullmatch(value)


@pytest.mark.parametrize("value", ["0", "00", "01", "abc", "a-b", "-", "A1"])
def test_build_identifier_valid(value):
    assert version.Version._BUILD_IDENTIFIER.fullmatch(value)


@pytest.mark.parametrize("value", ["", "a_b", "\u00e9", "a b", "a+b", "a.b"])
def test_build_identifier_invalid(value):
    assert not version.Version._BUILD_IDENTIFIER.fullmatch(value)


def test_validate_identifiers_accepts_valid():
    V = version.Version
    assert V._validate_identifiers("rc.1", V._PRERELEASE_IDENTIFIER, "thing") is None
    assert V._validate_identifiers("a", V._BUILD_IDENTIFIER, "thing") is None


@pytest.mark.parametrize("value", ["", "a..b", "a b", "01", ".a", "a."])
def test_validate_identifiers_rejects_invalid(value):
    V = version.Version
    with pytest.raises(ValueError, match="is not a valid thing"):
        V._validate_identifiers(value, V._PRERELEASE_IDENTIFIER, "thing")


@pytest.mark.parametrize(
    "a, b, expected",
    [
        ("rc.1", "rc.2", -1),
        ("rc.2", "rc.1", 1),
        ("rc.1", "rc.1", 0),
        ("rc.1", "rc.1.0", -1),
        ("rc.1.0", "rc.1", 1),
        ("alpha", "beta", -1),
        ("1", "alpha", -1),
        ("alpha", "1", 1),
        ("9", "10", -1),
        ("10", "9", 1),
        ("01", "1", 0),
        ("00", "0", 0),
        (None, None, 0),
        ("", None, 0),
        (None, "", 0),
        (None, "rc", -1),
        ("rc", None, 1),
        ("9" * 50, "9" * 49 + "8", 1),
        ("\u0663", "3", 0),
        ("alpha.1", "alpha.beta", -1),
        ("Alpha", "alpha", -1),
        ("rc10", "rc9", -1),
    ],
)
def test_nat_cmp(a, b, expected):
    assert version.Version._nat_cmp(a, b) == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        ("rc.1", "rc.2"),
        ("rc.9", "rc.10"),
        ("1", "2"),
        ("9", "10"),
        ("rc", "rc.0"),
        ("rc1", "rc1.0"),
        ("alpha.beta", "alpha.beta.0"),
        ("1.2.3", "1.2.4"),
        ("a.1.b", "a.1.b.0"),
        ("rc.09", "rc.10"),
    ],
)
def test_increment_prerelease(text, expected):
    assert version.Version._increment_prerelease(text) == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        ("build.9", "build.10"),
        ("build.99", "build.100"),
        ("a9", "a10"),
        ("9", "10"),
        ("b09", "b10"),
        ("x0099", "x0100"),
        ("1.2.3", "1.2.4"),
        ("abc", "abc"),
        ("", ""),
        ("build.9x", "build.10x"),
        ("rc1.5a2", "rc1.5a3"),
    ],
)
def test_increment_string(text, expected):
    assert version.Version._increment_string(text) == expected


def test_bump_major_minor_patch():
    v = version.Version.parse("3.4.5-rc.1+b")
    assert str(v.bump_major()) == "4.0.0"
    assert str(v.bump_minor()) == "3.5.0"
    assert str(v.bump_patch()) == "3.4.6"
    assert str(v) == "3.4.5-rc.1+b"


def test_bump_returns_subclass():
    v = SubVersion(1, 2, 3)
    assert type(v.bump_major()) is SubVersion
    assert type(v.bump_minor()) is SubVersion
    assert type(v.bump_patch()) is SubVersion
    assert type(v.bump_prerelease()) is SubVersion
    assert type(v.bump_build()) is SubVersion
    assert type(v.finalize_version()) is SubVersion
    assert type(v.replace(major=2)) is SubVersion
    assert type(v.next_version("prerelease")) is SubVersion


def test_bump_prerelease_defaults():
    v = version.Version.parse("3.4.5")
    assert v.bump_prerelease().prerelease == "rc.1"
    assert str(v.bump_prerelease()) == "3.4.5-rc.1"
    assert v.bump_prerelease("").prerelease == "1"
    assert v.bump_prerelease(None).prerelease == "rc.1"
    assert v.bump_prerelease("alpha").prerelease == "alpha.1"
    assert v.bump_prerelease("a.b").prerelease == "a.b.1"
    assert v.bump_prerelease(5).prerelease == "5.1"


def test_bump_prerelease_when_empty():
    v = version.Version.parse("3.4.5")
    assert str(v.bump_prerelease(bump_when_empty=True)) == "3.4.6-rc.1"
    assert str(v.bump_prerelease("", bump_when_empty=True)) == "3.4.6-1"
    assert str(v.bump_prerelease(None, True)) == "3.4.6-rc.1"


def test_bump_prerelease_existing():
    V = version.Version
    v = V.parse("3.4.5-rc.1")
    assert str(v.bump_prerelease()) == "3.4.5-rc.2"
    assert str(v.bump_prerelease(bump_when_empty=True)) == "3.4.5-rc.2"
    assert str(v.bump_prerelease("alpha")) == "3.4.5-rc.2"
    assert str(v.bump_prerelease("a b")) == "3.4.5-rc.2"
    assert str(V.parse("3.4.5-rc").bump_prerelease()) == "3.4.5-rc.0"
    assert str(V.parse("3.4.5-alpha.beta").bump_prerelease()) == "3.4.5-alpha.beta.0"


def test_bump_prerelease_drops_build():
    V = version.Version
    assert str(V.parse("1.2.3+b").bump_prerelease()) == "1.2.3-rc.1"
    assert str(V.parse("1.2.3-rc.1+b").bump_prerelease()) == "1.2.3-rc.2"


@pytest.mark.parametrize("token", ["a b", "01", "a..b", "a_b", "a+b", "\u00e9"])
def test_bump_prerelease_invalid_token(token):
    with pytest.raises(ValueError, match="prerelease token"):
        version.Version.parse("1.2.3").bump_prerelease(token)


def test_bump_build_defaults():
    v = version.Version.parse("3.4.5-rc.1")
    assert str(v.bump_build()) == "3.4.5-rc.1+build.1"
    assert str(v.bump_build(None)) == "3.4.5-rc.1+build.1"
    assert str(v.bump_build("")) == "3.4.5-rc.1+1"
    assert str(v.bump_build("ci")) == "3.4.5-rc.1+ci.1"
    assert str(v.bump_build("b5")) == "3.4.5-rc.1+b5.1"
    assert str(v.bump_build("01")) == "3.4.5-rc.1+01.1"
    assert v.bump_build(7).build == "7.1"


def test_bump_build_existing():
    V = version.Version
    assert str(V.parse("3.4.5-rc.1+build.9").bump_build()) == "3.4.5-rc.1+build.10"
    assert str(V.parse("3.4.5+7").bump_build()) == "3.4.5+8"
    assert str(V.parse("3.4.5+b.1").bump_build("a b")) == "3.4.5+b.2"
    assert str(V.parse("3.4.5+b.1").bump_build("other")) == "3.4.5+b.2"


def test_bump_build_without_digits_appends_zero():
    result = version.Version.parse("3.4.5-rc.1+alpha").bump_build()
    assert str(result) == "3.4.5-rc.1+alpha.0"


@pytest.mark.parametrize("token", ["a b", "a..b", "a_b", "a+b", "\u00e9", "a."])
def test_bump_build_invalid_token(token):
    with pytest.raises(ValueError, match="build token"):
        version.Version.parse("1.2.3").bump_build(token)


def test_bump_build_preserves_prerelease_and_version():
    v = version.Version.parse("1.2.3-rc.1")
    new = v.bump_build()
    assert new.prerelease == "rc.1"
    assert (new.major, new.minor, new.patch) == (1, 2, 3)
    assert v.build is None


def test_finalize_version():
    assert str(version.Version.parse("1.2.3-rc.5+b").finalize_version()) == "1.2.3"
    v = version.Version(1, 2, 3)
    assert v.finalize_version() == v
    assert v.finalize_version() is not v


@pytest.mark.parametrize(
    "a, b, expected",
    [
        ("1.0.0", "2.0.0", -1),
        ("2.0.0", "1.0.0", 1),
        ("2.0.0", "2.0.0", 0),
        ("1.2.0", "1.10.0", -1),
        ("1.0.2", "1.0.10", -1),
        ("1.0.0-rc.1", "1.0.0", -1),
        ("1.0.0", "1.0.0-rc.1", 1),
        ("1.0.0-rc.1", "1.0.0-rc.1", 0),
        ("1.0.0-rc.1", "1.0.0-rc.2", -1),
        ("1.0.0+a", "1.0.0+b", 0),
        ("1.0.0-rc.1+a", "1.0.0-rc.1+b", 0),
        ("1.0.0-alpha", "1.0.0-alpha.1", -1),
        ("1.0.0-alpha.1", "1.0.0-alpha.beta", -1),
        ("1.0.0-alpha.beta", "1.0.0-beta", -1),
        ("1.0.0-beta.2", "1.0.0-beta.11", -1),
        ("1.0.0-1", "1.0.0-alpha", -1),
        ("1.0.0-0", "1.0.0-rc", -1),
    ],
)
def test_compare_strings(a, b, expected):
    assert version.Version.parse(a).compare(b) == expected


def test_compare_precedence_sorting():
    ordered = [
        "1.0.0-alpha",
        "1.0.0-alpha.1",
        "1.0.0-alpha.beta",
        "1.0.0-beta",
        "1.0.0-beta.2",
        "1.0.0-beta.11",
        "1.0.0-rc.1",
        "1.0.0",
        "1.0.1",
        "1.1.0",
        "2.0.0",
    ]
    versions = [version.Version.parse(s) for s in ordered]
    assert sorted(reversed(versions)) == versions
    assert [str(v) for v in sorted(reversed(versions))] == ordered


def test_compare_other_types():
    v = version.Version(1, 2, 3)
    assert v.compare("1.2.4") == -1
    assert v.compare(b"1.2.2") == 1
    assert v.compare((1, 2, 3)) == 0
    assert v.compare([1, 2, 4]) == -1
    assert v.compare({"major": 1, "minor": 2, "patch": 3}) == 0
    assert v.compare(version.Version(1, 2, 3)) == 0
    assert v.compare(["1"]) == 1
    assert v.compare((1, 2, 3, "rc.1")) == 1


def test_compare_leading_zero_and_non_ascii_prerelease_equal():
    V = version.Version
    assert V(1, 0, 0, prerelease="01").compare(V(1, 0, 0, prerelease="1")) == 0
    assert V(1, 0, 0, prerelease="\u0663").compare(V(1, 0, 0, prerelease="3")) == 0


def test_compare_empty_prerelease_is_release():
    V = version.Version
    assert V(1, 0, 0, prerelease="").compare(V(1, 0, 0)) == 0
    assert V(1, 0, 0, prerelease="").compare(V(1, 0, 0, "rc")) == 1
    assert V(1, 0, 0, "rc").compare(V(1, 0, 0, prerelease="")) == -1


@pytest.mark.parametrize("bad", [None, 5, 1.5, object(), {1, 2}])
def test_compare_wrong_type_raises(bad):
    with pytest.raises(
        TypeError, match="Expected str, bytes, dict, tuple, list, or Version instance"
    ):
        version.Version(1).compare(bad)


def test_compare_invalid_inputs_raise():
    v = version.Version(1)
    with pytest.raises(ValueError):
        v.compare("not-a-version")
    with pytest.raises(ValueError):
        v.compare("1.2")
    with pytest.raises(TypeError):
        v.compare({"foo": 1})
    with pytest.raises(ValueError):
        v.compare((1, 2, "x"))
    with pytest.raises(TypeError):
        v.compare(())


@pytest.mark.parametrize(
    "other",
    [
        "1.2.4",
        b"1.2.4",
        (1, 2, 4),
        [1, 2, 4],
        {"major": 1, "minor": 2, "patch": 4},
        version.Version(1, 2, 4),
    ],
)
def test_comparison_operators_with_greater_other(other):
    v = version.Version(1, 2, 3)
    assert v < other
    assert v <= other
    assert v != other
    assert not v == other
    assert not v > other
    assert not v >= other


@pytest.mark.parametrize(
    "other",
    [
        "1.2.3",
        b"1.2.3",
        (1, 2, 3),
        [1, 2, 3],
        {"major": 1, "minor": 2, "patch": 3},
        version.Version(1, 2, 3),
    ],
)
def test_comparison_operators_with_equal_other(other):
    v = version.Version(1, 2, 3)
    assert v == other
    assert v <= other
    assert v >= other
    assert not v != other
    assert not v < other
    assert not v > other


@pytest.mark.parametrize(
    "other",
    [
        "1.2.2",
        b"1.2.2",
        (1, 2, 2),
        [1, 2, 2],
        {"major": 1, "minor": 2, "patch": 2},
        version.Version(1, 2, 2),
    ],
)
def test_comparison_operators_with_smaller_other(other):
    v = version.Version(1, 2, 3)
    assert v > other
    assert v >= other
    assert v != other
    assert not v < other
    assert not v <= other
    assert not v == other


def test_comparison_with_prerelease_collections():
    v = version.Version(1, 2, 3, "rc.1")
    assert v == (1, 2, 3, "rc.1")
    assert v < (1, 2, 3)
    assert v == {"major": 1, "minor": 2, "patch": 3, "prerelease": "rc.1"}


def test_comparison_ignores_build():
    V = version.Version
    assert V.parse("1.0.0+a") == V.parse("1.0.0+b")
    assert not V.parse("1.0.0+a") != V.parse("1.0.0+b")


def test_reflected_comparisons():
    v = version.Version(1, 2, 3)
    assert "1.2.3" == v
    assert "1.2.4" > v
    assert (1, 2, 4) > v
    assert [1, 2, 2] < v
    assert (1, 2, 3) == v
    assert {"major": 1, "minor": 2, "patch": 3} == v


@pytest.mark.parametrize("other", [1, 1.5, None, object(), {1, 2}, frozenset()])
def test_comparison_with_foreign_types(other):
    v = version.Version(1, 2, 3)
    assert not v == other
    assert v != other
    for op in ("__lt__", "__le__", "__gt__", "__ge__", "__eq__", "__ne__"):
        assert getattr(v, op)(other) is NotImplemented
    with pytest.raises(TypeError):
        v < other
    with pytest.raises(TypeError):
        v >= other


@pytest.mark.parametrize(
    "other",
    [
        {},
        {"foo": 1},
        {"major": "x"},
        (),
        [],
        (1, "x"),
        (-1,),
        (1, 2, 3, None, None, None),
        {"major": -1},
    ],
)
def test_comparison_with_invalid_collections(other):
    v = version.Version(1, 2, 3)
    assert not v == other
    assert v != other
    assert v.__eq__(other) is NotImplemented
    assert v.__ne__(other) is NotImplemented
    with pytest.raises(TypeError):
        v < other
    with pytest.raises(TypeError):
        v > other


@pytest.mark.parametrize("other", ["not-a-version", "1.2", b"bad", ""])
def test_comparison_with_invalid_strings_raises(other):
    v = version.Version(1)
    with pytest.raises(ValueError):
        v == other
    with pytest.raises(ValueError):
        v < other


def test_comparator_preserves_names():
    for name in ("__eq__", "__ne__", "__lt__", "__le__", "__gt__", "__ge__"):
        assert getattr(version.Version, name).__name__ == name


def test_subclass_comparison():
    assert SubVersion(1, 2, 3) == SubVersion(1, 2, 3)
    assert SubVersion(1, 2, 3) < SubVersion(1, 2, 4)
    assert SubVersion(1, 2, 3) == "1.2.3"


def test_getitem_single_index():
    v = version.Version(3, 4, 5)
    assert (v[0], v[1], v[2]) == (3, 4, 5)


def test_getitem_defined_prerelease_and_build():
    v = version.Version(3, 4, 5, "rc.1", "b.2")
    assert v[3] == "rc.1"
    assert v[4] == "b.2"
    assert v[3:5] == ("rc.1", "b.2")
    assert v[:] == (3, 4, 5, "rc.1", "b.2")
    assert v[2:4] == (5, "rc.1")


def test_getitem_slices():
    v = version.Version(3, 4, 5)
    assert v[:3] == (3, 4, 5)
    assert v[:4] == (3, 4, 5)
    assert v[0:2] == (3, 4)
    assert v[1:3] == (4, 5)
    assert v[:1] == 3
    assert v[1:2] == 4
    assert v[::2] == (3, 5)
    assert v[::-1] == (5, 4, 3)


def test_getitem_index_like_objects():
    v = version.Version(3, 4, 5)
    assert v[IndexLike(1)] == 4
    assert v[True] == 4
    assert v[IndexLike(0):IndexLike(2)] == (3, 4)


@pytest.mark.parametrize(
    "index",
    [3, 4, 5, 10, slice(3, None), slice(0, 0), slice(None, 0), slice(3, 5)],
)
def test_getitem_undefined_part_raises(index):
    with pytest.raises(IndexError, match="Version part undefined"):
        version.Version(3, 4, 5)[index]


@pytest.mark.parametrize(
    "index",
    [-1, -5, slice(-1, None), slice(None, -1), slice(-2, -1)],
)
def test_getitem_negative_raises(index):
    with pytest.raises(IndexError, match="cannot be negative"):
        version.Version(3, 4, 5)[index]


@pytest.mark.parametrize(
    "index", [1.5, "0", None, slice(0, 1.5), slice(1.5, 2), slice("a", 2)]
)
def test_getitem_wrong_index_type_raises(index):
    with pytest.raises(TypeError):
        version.Version(3, 4, 5)[index]


@pytest.mark.parametrize(
    "expr, expected",
    [
        (">=1.0.0", True),
        (">1.0.0", True),
        ("<3.0.0", True),
        ("<=2.0.0", True),
        ("==2.0.0", True),
        ("!=1.0.0", True),
        ("2.0.0", True),
        (">=2.0.0", True),
        ("<=3.0.0", True),
        (">=3.0.0", False),
        (">2.0.0", False),
        ("<2.0.0", False),
        ("<=1.0.0", False),
        ("==1.0.0", False),
        ("!=2.0.0", False),
        ("1.0.0", False),
    ],
)
def test_match(expr, expected):
    assert version.Version.parse("2.0.0").match(expr) is expected


def test_match_with_prerelease():
    v = version.Version.parse("1.0.0-rc.1")
    assert v.match("<1.0.0")
    assert v.match(">=1.0.0-rc.1")
    assert not v.match(">1.0.0")


@pytest.mark.parametrize(
    "expr", ["", "=1.0.0", "~1.0.0", "!1.0.0", "^1.0.0", "v1.0.0", " 1.0.0", "=>1.0.0"]
)
def test_match_invalid_expression(expr):
    with pytest.raises(
        ValueError, match="match_expr parameter should be in format"
    ):
        version.Version.parse("2.0.0").match(expr)


@pytest.mark.parametrize(
    "expr", [">=abc", ">", "<", "==", "!=", ">=1.2", "1.2", ">1"]
)
def test_match_invalid_version_part(expr):
    with pytest.raises(ValueError):
        version.Version.parse("2.0.0").match(expr)


def test_replace_parts():
    v = version.Version.parse("1.2.3-rc.1+b")
    assert str(v.replace(major=2)) == "2.2.3-rc.1+b"
    assert str(v.replace(minor=5)) == "1.5.3-rc.1+b"
    assert str(v.replace(patch=9)) == "1.2.9-rc.1+b"
    assert str(v.replace(prerelease="beta")) == "1.2.3-beta+b"
    assert str(v.replace(build="c")) == "1.2.3-rc.1+c"
    assert str(v.replace(prerelease=None, build=None)) == "1.2.3"
    assert str(v.replace(major="5")) == "5.2.3-rc.1+b"
    assert str(v.replace(build=5)) == "1.2.3-rc.1+5"
    assert str(v.replace()) == "1.2.3-rc.1+b"
    assert str(v) == "1.2.3-rc.1+b"


def test_replace_unknown_keys():
    with pytest.raises(
        TypeError, match=r"replace\(\) got 1 unexpected keyword argument\(s\): foo"
    ):
        version.Version(1).replace(foo=1)
    with pytest.raises(
        TypeError, match=r"replace\(\) got 2 unexpected keyword argument\(s\)"
    ):
        version.Version(1).replace(foo=1, bar=2)


def test_replace_known_key_with_bad_value():
    with pytest.raises(TypeError) as info:
        version.Version(1).replace(major=None)
    assert "replace() got" not in str(info.value)
    with pytest.raises(ValueError):
        version.Version(1).replace(major=-1)
    with pytest.raises(ValueError):
        version.Version(1).replace(minor="x")


@pytest.mark.parametrize(
    "a, b, expected",
    [
        ("1.0.0", "1.1.0", True),
        ("1.1.0", "1.0.0", False),
        ("1.0.0", "2.0.0", False),
        ("2.0.0", "1.0.0", False),
        ("1.0.0", "1.0.0", True),
        ("1.0.0", "1.0.5", True),
        ("1.0.5", "1.0.0", True),
        ("1.0.0", "1.0.0-rc.1", False),
        ("1.0.0-rc.1", "1.1.0-rc.1", True),
        ("1.0.0", "1.0.0+build", True),
        ("0.1.0", "0.1.0", True),
        ("0.1.0", "0.1.1", False),
        ("0.1.0", "0.2.0", False),
        ("0.1.1", "0.1.0", False),
        ("0.1.0+a", "0.1.0+b", True),
        ("0.0.0", "0.0.0", True),
        ("0.1.0-rc.1", "0.1.0-rc.1", True),
        ("0.1.0-rc.1", "0.1.0", False),
        ("0.1.0", "1.0.0", False),
    ],
)
def test_is_compatible(a, b, expected):
    result = version.Version.parse(a).is_compatible(version.Version.parse(b))
    assert result is expected


@pytest.mark.parametrize("bad", ["1.0.0", None, (1, 0, 0), 1, {"major": 1}])
def test_is_compatible_wrong_type(bad):
    with pytest.raises(TypeError, match="Expected a Version type but got"):
        version.Version(1, 0, 0).is_compatible(bad)


@pytest.mark.parametrize("part", ["", "build", "foo", "Major", "MAJOR", None])
def test_next_version_invalid_part(part):
    with pytest.raises(ValueError, match="Invalid part"):
        version.Version.parse("1.2.3").next_version(part)


def test_next_version_invalid_part_message():
    with pytest.raises(ValueError) as info:
        version.Version.parse("1.2.3").next_version("build")
    assert "('major', 'minor', 'patch', 'prerelease')" in str(info.value)
    assert "'build'" in str(info.value)


@pytest.mark.parametrize(
    "start, part, expected",
    [
        ("1.2.3", "major", "2.0.0"),
        ("1.2.3", "minor", "1.3.0"),
        ("1.2.3", "patch", "1.2.4"),
        ("1.2.3+b", "patch", "1.2.4"),
        ("0.1.4", "prerelease", "0.1.5-rc.1"),
        ("1.2.3-rc.1+b", "patch", "1.2.3"),
        ("1.2.3-rc.1", "minor", "1.3.0"),
        ("1.2.0-rc.1", "minor", "1.2.0"),
        ("1.2.0-rc.1+x", "minor", "1.2.0"),
        ("1.2.3-rc.1", "major", "2.0.0"),
        ("1.2.0-rc.1", "major", "2.0.0"),
        ("1.0.3-rc.1", "major", "2.0.0"),
        ("1.0.0-rc.1", "major", "1.0.0"),
        ("2.0.0-rc.1+x", "major", "2.0.0"),
    ],
)
def test_next_version_main_parts(start, part, expected):
    assert str(version.Version.parse(start).next_version(part)) == expected


def test_next_version_empty_prerelease_treated_as_release():
    v = version.Version(1, 2, 3, prerelease="")
    assert str(v.next_version("patch")) == "1.2.4"


@pytest.mark.parametrize(
    "start, token, expected",
    [
        ("1.2.3-rc.1", "rc", "1.2.3-rc.2"),
        ("1.2.3-rc.1+build", "rc", "1.2.3-rc.2"),
        ("1.2.3-rc", "rc", "1.2.3-rc.0"),
        ("1.2.3-rc3", "rc", "1.2.3-rc4"),
        ("1.2.3-rc3+meta", "rc", "1.2.3-rc4"),
        ("1.2.3-rc9", "rc", "1.2.4-rc10"),
        ("1.2.3-rc.1", "alpha", "1.2.4-alpha.1"),
        ("1.2.3-alpha.1", "rc", "1.2.3-rc.1"),
        ("1.2.3-beta.1", "rc", "1.2.3-rc.1"),
        ("1.2.3-1", "rc", "1.2.3-rc.1"),
        ("1.2.3-rc.1", "", "1.2.3-rc.2"),
        ("1.2.3-rc.1", None, "1.2.3-rc.2"),
        ("1.2.3", "rc", "1.2.4-rc.1"),
        ("1.2.3", "alpha", "1.2.4-alpha.1"),
        ("1.2.3", "", "1.2.4-1"),
        ("1.2.3", None, "1.2.4-rc.1"),
        ("1.2.3+b", "rc", "1.2.4-rc.1"),
    ],
)
def test_next_version_prerelease(start, token, expected):
    result = version.Version.parse(start).next_version("prerelease", token)
    assert str(result) == expected


def test_next_version_prerelease_default_token():
    V = version.Version
    assert str(V.parse("1.2.3-rc.1").next_version("prerelease")) == "1.2.3-rc.2"
    assert str(V.parse("1.2.3-rc9").next_version("prerelease")) == "1.2.4-rc10"


def test_next_version_results_are_greater():
    start = version.Version.parse("1.2.3-rc9")
    assert start.next_version("prerelease") > start
    start = version.Version.parse("1.2.3-rc.1")
    assert start.next_version("prerelease", "alpha") > start


@pytest.mark.parametrize("start", ["1.2.3", "1.2.3-rc.1", "1.2.3-rc3"])
@pytest.mark.parametrize("token", ["a b", "01", "a_b", "a..b"])
def test_next_version_invalid_token(start, token):
    with pytest.raises(ValueError, match="prerelease token"):
        version.Version.parse(start).next_version("prerelease", token)


def test_next_version_leaves_original_untouched():
    v = version.Version.parse("1.2.3-rc9+b")
    v.next_version("prerelease")
    v.next_version("patch")
    assert str(v) == "1.2.3-rc9+b"


def test_extreme_values_roundtrip():
    big = 10**30
    v = version.Version(big, big, big, "9" * 50, "9" * 50)
    assert version.Version.parse(str(v)) == v
    assert v.bump_major().major == big + 1