
import pytest
import semver.version as version_module
from semver.version import Version, VersionInfo


@pytest.fixture
def version():
    return Version(1, 2, 3)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("1.2.3", (1, 2, 3, None, None)),
        ("0.0.0", (0, 0, 0, None, None)),
        ("1.2.3-alpha", (1, 2, 3, "alpha", None)),
        ("1.2.3-alpha.1+build.5", (1, 2, 3, "alpha.1", "build.5")),
        ("1.2.3+build", (1, 2, 3, None, "build")),
        ("10.20.30", (10, 20, 30, None, None)),
    ],
)
def test_parse_valid_versions(value, expected):
    assert Version.parse(value).to_tuple() == expected


@pytest.mark.parametrize(
    "value",
    [
        "",
        "1",
        "1.2",
        "1.2.3.4",
        "01.2.3",
        "1.02.3",
        "1.2.03",
        "-1.2.3",
        "1.-2.3",
        "1.2.-3",
        "1.2.3-",
        "1.2.3+",
        "1.2.3-alpha..beta",
        "1.2.3+build..meta",
        "1.2.3-alpha_1",
        "1.2.3+build_meta",
        "1.2.3-alpha+",
        "1.2.3+build-alpha",
        "v1.2.3",
        " 1.2.3",
        "1.2.3 ",
        "1.2.3\n",
    ],
)
def test_parse_invalid_versions(value):
    with pytest.raises(ValueError):
        Version.parse(value)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("1", (1, 0, 0, None, None)),
        ("1.2", (1, 2, 0, None, None)),
        ("1.2.3", (1, 2, 3, None, None)),
        ("1-alpha", (1, 0, 0, "alpha", None)),
        ("1.2-alpha+build", (1, 2, 0, "alpha", "build")),
    ],
)
def test_parse_optional_minor_and_patch(value, expected):
    assert Version.parse(value, optional_minor_and_patch=True).to_tuple() == expected


@pytest.mark.parametrize(
    "value",
    [
        "01",
        "1.02",
        "1.2.03",
        "1.",
        ".1",
        "1..2",
        "1.2.",
        "1.2.3.4",
        "1.2.3-alpha..beta",
    ],
)
def test_parse_rejects_invalid_optional_versions(value):
    with pytest.raises(ValueError):
        Version.parse(value, optional_minor_and_patch=True)


def test_parse_bytes():
    assert Version.parse(b"1.2.3") == Version(1, 2, 3)


def test_parse_invalid_utf8_bytes():
    with pytest.raises(UnicodeDecodeError):
        Version.parse(b"\xff")


@pytest.mark.parametrize("value", [None, 123, 1.2, [], {}, object()])
def test_parse_rejects_unsupported_types(value):
    with pytest.raises(TypeError):
        Version.parse(value)


def test_parse_uses_subclass():
    class CustomVersion(Version):
        pass

    result = CustomVersion.parse("1.2.3")
    assert isinstance(result, CustomVersion)


def test_parse_native_backend_success(monkeypatch):
    monkeypatch.setattr(
        version_module,
        "_native_parse_parts",
        lambda value: (1, 2, 3, "alpha", "build"),
    )
    result = Version.parse("1.2.3-alpha+build")
    assert result == Version(1, 2, 3, "alpha", "build")


def test_parse_native_backend_value_error_falls_back(monkeypatch):
    monkeypatch.setattr(
        version_module,
        "_native_parse_parts",
        lambda value: (_ for _ in ()).throw(ValueError("native failure")),
    )
    assert Version.parse("1.2.3") == Version(1, 2, 3)


def test_parse_native_backend_not_used_for_optional_parts(monkeypatch):
    def fail(value):
        raise AssertionError("native parser should not be called")

    monkeypatch.setattr(version_module, "_native_parse_parts", fail)
    assert Version.parse("1", optional_minor_and_patch=True) == Version(1)


def test_constructor_defaults():
    result = Version(2)
    assert result.to_tuple() == (2, 0, 0, None, None)


def test_constructor_converts_integer_like_values():
    result = Version("2", "3", "4", 5, 6)
    assert result.to_tuple() == (2, 3, 4, "5", "6")


@pytest.mark.parametrize(
    ("args", "message"),
    [
        ((-1,), "'major' is negative"),
        ((1, -1), "'minor' is negative"),
        ((1, 2, -1), "'patch' is negative"),
    ],
)
def test_constructor_rejects_negative_parts(args, message):
    with pytest.raises(ValueError, match=message):
        Version(*args)


@pytest.mark.parametrize(
    "args",
    [
        ("not-an-int",),
        (1, "invalid"),
        (1, 2, "invalid"),
    ],
)
def test_constructor_rejects_non_integer_parts(args):
    with pytest.raises(ValueError):
        Version(*args)


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("major", 1),
        ("minor", 2),
        ("patch", 3),
        ("prerelease", "alpha"),
        ("build", "build.1"),
    ],
)
def test_readonly_properties(name, expected):
    assert getattr(Version(1, 2, 3, "alpha", "build.1"), name) == expected


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("major", 2),
        ("minor", 3),
        ("patch", 4),
        ("prerelease", "beta"),
        ("build", "build.2"),
    ],
)
def test_properties_are_readonly(name, value):
    instance = Version(1, 2, 3, "alpha", "build.1")
    with pytest.raises(AttributeError, match="readonly"):
        setattr(instance, name, value)


def test_slots_prevent_arbitrary_attributes(version):
    with pytest.raises(AttributeError):
        version.extra = "value"


def test_names():
    assert Version.NAMES == ("major", "minor", "patch", "prerelease", "build")


def test_to_tuple():
    assert Version(5, 3, 1).to_tuple() == (5, 3, 1, None, None)


def test_to_dict():
    assert Version(3, 2, 1).to_dict() == {
        "major": 3,
        "minor": 2,
        "patch": 1,
        "prerelease": None,
        "build": None,
    }


def test_to_dict_preserves_key_order():
    assert list(Version(1).to_dict()) == [
        "major",
        "minor",
        "patch",
        "prerelease",
        "build",
    ]


def test_iteration():
    assert tuple(Version(1, 2, 3, "alpha", "build")) == (
        1,
        2,
        3,
        "alpha",
        "build",
    )


def test_repr():
    assert repr(Version(1, 2, 3)) == (
        "Version(major=1, minor=2, patch=3, prerelease=None, build=None)"
    )


def test_str_without_metadata():
    assert str(Version(1, 2, 3)) == "1.2.3"


def test_str_with_prerelease():
    assert str(Version(1, 2, 3, "alpha.1")) == "1.2.3-alpha.1"


def test_str_with_build():
    assert str(Version(1, 2, 3, None, "build.5")) == "1.2.3+build.5"


def test_str_with_both_metadata():
    assert str(Version(1, 2, 3, "alpha", "build")) == "1.2.3-alpha+build"


def test_hash_ignores_build_metadata():
    assert hash(Version(1, 2, 3, "alpha", "build.1")) == hash(
        Version(1, 2, 3, "alpha", "build.2")
    )


def test_hash_includes_prerelease():
    assert hash(Version(1, 2, 3, "alpha")) != hash(Version(1, 2, 3, "beta"))


def test_versions_can_be_used_as_dictionary_keys():
    mapping = {Version(1, 2, 3): "value"}
    assert mapping[Version(1, 2, 3)] == "value"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("", True),
        ("0", True),
        ("1", True),
        ("9", True),
        ("10", True),
        ("a", False),
        ("alpha", False),
        ("rc.1", False),
        ("alpha.10", False),
        ("alpha10", False),
        ("123alpha", False),
    ],
)
def test_validate_identifiers(value, expected):
    if expected:
        assert Version._validate_identifiers(
            value, Version._PRERELEASE_IDENTIFIER, "prerelease"
        ) is None
    else:
        with pytest.raises(ValueError):
            Version._validate_identifiers(
                value, Version._PRERELEASE_IDENTIFIER, "prerelease"
            )


@pytest.mark.parametrize(
    "value",
    ["", "alpha_beta", "alpha beta", "alpha+", "alpha..beta", "alpha."],
)
def test_validate_prerelease_identifiers_rejects_invalid_values(value):
    with pytest.raises(ValueError):
        Version._validate_identifiers(
            value, Version._PRERELEASE_IDENTIFIER, "prerelease"
        )


@pytest.mark.parametrize(
    "value",
    ["build", "build.1", "ABC", "123", "a-b", "0"],
)
def test_validate_build_identifiers(value):
    assert Version._validate_identifiers(
        value, Version._BUILD_IDENTIFIER, "build"
    ) is None


@pytest.mark.parametrize(
    "value",
    ["", "build..1", "build_1", "build 1", "build+", "build."],
)
def test_validate_build_identifiers_rejects_invalid_values(value):
    with pytest.raises(ValueError):
        Version._validate_identifiers(value, Version._BUILD_IDENTIFIER, "build")


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        (None, None, 0),
        (None, "alpha", -1),
        ("alpha", None, 1),
        ("alpha", "beta", -1),
        ("beta", "alpha", 1),
        ("alpha", "alpha", 0),
        ("alpha.1", "alpha.2", -1),
        ("alpha.2", "alpha.1", 1),
        ("alpha", "alpha.1", -1),
        ("alpha.1", "alpha", 1),
        ("1", "2", -1),
        ("2", "1", 1),
        ("alpha.10", "alpha.2", 1),
        ("alpha.02", "alpha.2", 0),
        ("alpha.0", "alpha.00", 0),
        ("alpha.10", "alpha.beta", -1),
        ("alpha.beta", "alpha.10", 1),
    ],
)
def test_natural_prerelease_comparison(a, b, expected):
    assert Version._nat_cmp(a, b) == expected


def test_natural_comparison_handles_large_numeric_identifiers():
    a = "alpha." + "9" * 500
    b = "alpha.1" + "0" * 500
    assert Version._nat_cmp(a, b) == -1


def test_natural_comparison_handles_unicode_digits():
    assert Version._nat_cmp("alpha.٢", "alpha.2") == 0


def test_increment_prerelease_numeric():
    assert Version._increment_prerelease("rc.1") == "rc.2"


def test_increment_prerelease_without_dot():
    assert Version._increment_prerelease("rc9") == "rc10"


def test_increment_prerelease_without_numeric_suffix():
    assert Version._increment_prerelease("alpha") == "alpha.0"


def test_increment_prerelease_empty_string():
    assert Version._increment_prerelease("") == ".0"


def test_increment_prerelease_leading_zeroes():
    assert Version._increment_prerelease("rc.009") == "rc.10"


def test_increment_string_with_number():
    assert Version._increment_string("build.9") == "build.10"


def test_increment_string_without_number():
    assert Version._increment_string("build") == "build"


def test_increment_string_multiple_numbers():
    assert Version._increment_string("build.2.9") == "build.2.10"


def test_increment_string_zero_padding():
    assert Version._increment_string("build.009") == "build.10"


def test_increment_string_empty():
    assert Version._increment_string("") == ""


def test_bump_major(version):
    result = version.bump_major()
    assert result == Version(2, 0, 0)
    assert version == Version(1, 2, 3)


def test_bump_minor(version):
    result = version.bump_minor()
    assert result == Version(1, 3, 0)
    assert version == Version(1, 2, 3)


def test_bump_patch(version):
    result = version.bump_patch()
    assert result == Version(1, 2, 4)
    assert version == Version(1, 2, 3)


def test_bump_methods_preserve_subclass():
    class CustomVersion(Version):
        pass

    instance = CustomVersion(1, 2, 3)
    assert isinstance(instance.bump_major(), CustomVersion)
    assert isinstance(instance.bump_minor(), CustomVersion)
    assert isinstance(instance.bump_patch(), CustomVersion)


@pytest.mark.parametrize(
    ("initial", "token", "bump_when_empty", "expected"),
    [
        (Version(1, 2, 3), "rc", False, "1.2.3-rc.1"),
        (Version(1, 2, 3), "", False, "1.2.3-1"),
        (Version(1, 2, 3), None, False, "1.2.3-rc.1"),
        (Version(1, 2, 3, "rc.1"), "beta", False, "1.2.3-rc.2"),
        (Version(1, 2, 3, "alpha"), "rc", False, "1.2.3-alpha.0"),
        (Version(1, 2, 3), "rc", True, "1.2.4-rc.1"),
        (Version(1, 2, 3), "", True, "1.2.4-1"),
        (Version(1, 2, 3), None, True, "1.2.4-rc.1"),
    ],
)
def test_bump_prerelease(initial, token, bump_when_empty, expected):
    assert str(
        initial.bump_prerelease(token, bump_when_empty=bump_when_empty)
    ) == expected


@pytest.mark.parametrize("token", ["", "alpha_beta", "alpha beta", "a..b", "."])
def test_bump_prerelease_rejects_invalid_token(token):
    with pytest.raises(ValueError):
        Version(1, 2, 3).bump_prerelease(token)


def test_bump_prerelease_converts_non_string_token():
    assert str(Version(1, 2, 3).bump_prerelease(12)) == "1.2.3-12.1"


def test_bump_prerelease_existing_value_ignores_token():
    assert str(Version(1, 2, 3, "alpha.1").bump_prerelease("invalid_token")) == (
        "1.2.3-alpha.2"
    )


@pytest.mark.parametrize(
    ("initial", "token", "expected"),
    [
        (Version(1, 2, 3), "build", "1.2.3+build.1"),
        (Version(1, 2, 3), "", "1.2.3+1"),
        (Version(1, 2, 3), None, "1.2.3+build.1"),
        (Version(1, 2, 3, None, "build.9"), "ignored", "1.2.3+build.10"),
        (Version(1, 2, 3, None, "alpha"), "ignored", "1.2.3+alpha.0"),
        (Version(1, 2, 3, None, "build9"), "ignored", "1.2.3+build10"),
        (Version(1, 2, 3, None, "build.009"), "ignored", "1.2.3+build.10"),
    ],
)
def test_bump_build(initial, token, expected):
    assert str(initial.bump_build(token)) == expected


@pytest.mark.parametrize("token", ["", "build_name", "build name", "a..b", "."])
def test_bump_build_rejects_invalid_token(token):
    with pytest.raises(ValueError):
        Version(1, 2, 3).bump_build(token)


def test_bump_build_converts_non_string_token():
    assert str(Version(1, 2, 3).bump_build(12)) == "1.2.3+12.1"


def test_bump_build_preserves_prerelease():
    result = Version(1, 2, 3, "rc.1").bump_build()
    assert result.prerelease == "rc.1"
    assert result.build == "build.1"


def test_compare_equal_versions():
    assert Version(1, 2, 3).compare(Version(1, 2, 3)) == 0


def test_compare_major_minor_patch():
    assert Version(1, 2, 3).compare(Version(2, 0, 0)) == -1
    assert Version(2, 0, 0).compare(Version(1, 9, 9)) == 1
    assert Version(1, 2, 3).compare(Version(1, 3, 0)) == -1
    assert Version(1, 3, 0).compare(Version(1, 2, 9)) == 1
    assert Version(1, 2, 3).compare(Version(1, 2, 4)) == -1
    assert Version(1, 2, 4).compare(Version(1, 2, 3)) == 1


def test_compare_prerelease_precedes_release():
    assert Version(1, 0, 0, "alpha").compare(Version(1, 0, 0)) == -1
    assert Version(1, 0, 0).compare(Version(1, 0, 0, "alpha")) == 1


def test_compare_prerelease_natural_order():
    assert Version(1, 0, 0, "alpha.2").compare(
        Version(1, 0, 0, "alpha.10")
    ) == -1


def test_compare_build_metadata_is_ignored():
    assert Version(1, 2, 3, "alpha", "build.1").compare(
        Version(1, 2, 3, "alpha", "build.2")
    ) == 0


@pytest.mark.parametrize(
    "other",
    [
        "1.2.3",
        b"1.2.3",
        {"major": 1, "minor": 2, "patch": 3},
        (1, 2, 3),
        [1, 2, 3],
        Version(1, 2, 3),
    ],
)
def test_compare_supported_operand_types(other):
    assert Version(1, 2, 3).compare(other) == 0


@pytest.mark.parametrize("other", [None, 123, 1.2, object(), set([1, 2, 3])])
def test_compare_rejects_unsupported_operand_types(other):
    with pytest.raises(TypeError):
        Version(1, 2, 3).compare(other)


def test_compare_rejects_invalid_string():
    with pytest.raises(ValueError):
        Version(1, 2, 3).compare("invalid")


def test_compare_rejects_invalid_dictionary():
    with pytest.raises(TypeError):
        Version(1, 2, 3).compare({"unknown": 1})


def test_compare_rejects_invalid_tuple():
    with pytest.raises(TypeError):
        Version(1, 2, 3).compare((1, 2, 3, 4, 5, 6))


@pytest.mark.parametrize(
    ("left", "right", "expected"),
    [
        ("1.2.3", "1.2.3", True),
        ("1.2.3", "1.2.4", False),
        ("1.2.3", "1.2.4", True),
    ],
)
def test_comparison_operators(left, right, expected):
    a = Version.parse(left)
    b = Version.parse(right)
    assert (a == b) is (a.compare(b) == 0)
    assert (a != b) is (a.compare(b) != 0)
    assert (a < b) is (a.compare(b) < 0)
    assert (a <= b) is (a.compare(b) <= 0)
    assert (a > b) is (a.compare(b) > 0)
    assert (a >= b) is (a.compare(b) >= 0)


@pytest.mark.parametrize(
    "other",
    [
        None,
        123,
        1.5,
        object(),
        set(),
    ],
)
def test_comparison_operators_return_not_implemented_for_unsupported_types(other):
    instance = Version(1, 2, 3)
    assert Version.__eq__(instance, other) is NotImplemented
    assert Version.__ne__(instance, other) is NotImplemented
    assert Version.__lt__(instance, other) is NotImplemented
    assert Version.__le__(instance, other) is NotImplemented
    assert Version.__gt__(instance, other) is NotImplemented
    assert Version.__ge__(instance, other) is NotImplemented


@pytest.mark.parametrize(
    ("other", "expected"),
    [
        ((1, 2, 3), True),
        ([1, 2, 3], True),
        ({"major": 1, "minor": 2, "patch": 3}, True),
        ((1, 2), False),
        ([1, 2, 3, 4, 5, 6], False),
        ({"unknown": 1}, False),
        ({"major": -1}, False),
    ],
)
def test_equality_with_collections(other, expected):
    assert (Version(1, 2, 3) == other) is expected


def test_version_info_alias():
    assert VersionInfo is Version


@pytest.mark.parametrize(
    ("part", "expected"),
    [
        (0, 1),
        (1, 2),
        (2, 3),
        (3, "alpha"),
        (4, "build"),
    ],
)
def test_getitem_integer_indices(part, expected):
    assert Version(1, 2, 3, "alpha", "build")[part] == expected


def test_getitem_missing_prerelease():
    with pytest.raises(IndexError, match="Version part undefined"):
        _ = Version(1, 2, 3)[3]


def test_getitem_missing_build():
    with pytest.raises(IndexError, match="Version part undefined"):
        _ = Version(1, 2, 3)[4]


def test_getitem_out_of_range():
    with pytest.raises(IndexError, match="Version part undefined"):
        _ = Version(1, 2, 3)[5]


@pytest.mark.parametrize("index", [-1, -2, -5])
def test_getitem_negative_integer_index(index):
    with pytest.raises(IndexError, match="cannot be negative"):
        _ = Version(1, 2, 3)[index]


def test_getitem_slice_all_parts():
    assert Version(1, 2, 3, "alpha", "build")[:] == (
        1,
        2,
        3,
        "alpha",
        "build",
    )


def test_getitem_slice_without_metadata():
    assert Version(1, 2, 3)[:3] == (1, 2, 3)


def test_getitem_slice_with_missing_parts():
    assert Version(1, 2, 3)[3:5] == ()


def test_getitem_slice_filters_missing_parts():
    assert Version(1, 2, 3, "alpha")[2:5] == (3, "alpha")


def test_getitem_slice_single_result_returns_scalar():
    assert Version(1, 2, 3)[1:2] == 2


def test_getitem_slice_empty_result():
    assert Version(1, 2, 3)[5:5] == ()


def test_getitem_slice_negative_start():
    with pytest.raises(IndexError, match="cannot be negative"):
        _ = Version(1, 2, 3)[-1:3]


def test_getitem_slice_negative_stop():
    with pytest.raises(IndexError, match="cannot be negative"):
        _ = Version(1, 2, 3)[0:-1]


def test_getitem_slice_accepts_index_objects():
    class IndexValue:
        def __index__(self):
            return 1

    assert Version(1, 2, 3)[IndexValue()] == 2
    assert Version(1, 2, 3)[IndexValue():3] == (2, 3)


def test_getitem_rejects_invalid_index():
    with pytest.raises(TypeError):
        _ = Version(1, 2, 3)["1"]


def test_getitem_rejects_invalid_slice_bound():
    with pytest.raises(TypeError):
        _ = Version(1, 2, 3)["1":3]


def test_finalize_version():
    result = Version(1, 2, 3, "rc.5", "build.10").finalize_version()
    assert result == Version(1, 2, 3)
    assert result.prerelease is None
    assert result.build is None


def test_finalize_version_does_not_mutate_original():
    original = Version(1, 2, 3, "rc.5", "build.10")
    original.finalize_version()
    assert original.prerelease == "rc.5"
    assert original.build == "build.10"


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        (">1.2.2", True),
        (">1.2.3", False),
        ("<1.2.4", True),
        ("<1.2.3", False),
        (">=1.2.3", True),
        (">=1.2.4", False),
        ("<=1.2.3", True),
        ("<=1.2.2", False),
        ("==1.2.3", True),
        ("!=1.2.3", False),
        ("!=1.2.4", True),
        ("1.2.3", True),
        ("1.2.4", False),
    ],
)
def test_match(expression, expected):
    assert Version(1, 2, 3).match(expression) is expected


@pytest.mark.parametrize(
    "expression",
    [
        "",
        "abc",
        "=1.2.3",
        "!1.2.3",
        "=>1.2.3",
        ">= ",
        "v1.2.3",
    ],
)
def test_match_invalid_expression(expression):
    with pytest.raises(ValueError):
        Version(1, 2, 3).match(expression)


def test_match_invalid_version_expression():
    with pytest.raises(ValueError):
        Version(1, 2, 3).match(">=invalid")


def test_match_prerelease_versions():
    assert Version(1, 2, 3, "alpha").match("<1.2.3") is True
    assert Version(1, 2, 3).match(">1.2.3-alpha") is True


@pytest.mark.parametrize(
    ("part", "expected"),
    [
        ("major", "2.0.0"),
        ("minor", "1.3.0"),
        ("patch", "1.2.4"),
        ("prerelease", "1.2.3-rc.1"),
    ],
)
def test_next_version_main_parts(version, part, expected):
    assert str(version.next_version(part)) == expected


@pytest.mark.parametrize("part", ["build", "unknown", "", "PRERELEASE"])
def test_next_version_invalid_part(version, part):
    with pytest.raises(ValueError, match="Invalid part"):
        version.next_version(part)


def test_next_version_prerelease_from_release():
    assert str(Version(1, 2, 3).next_version("prerelease")) == "1.2.4-rc.1"


def test_next_version_prerelease_custom_token():
    assert str(Version(1, 2, 3).next_version("prerelease", "beta")) == (
        "1.2.4-beta.1"
    )


def test_next_version_prerelease_advances_existing_matching_token():
    assert str(Version(1, 2, 3, "rc.1").next_version("prerelease")) == (
        "1.2.3-rc.2"
    )


def test_next_version_prerelease_advances_old_style_counter():
    assert str(Version(1, 2, 3, "rc9").next_version("prerelease")) == (
        "1.2.4-rc10"
    )


def test_next_version_prerelease_with_custom_old_style_counter():
    assert str(
        Version(1, 2, 3, "alpha3").next_version("prerelease", "alpha")
    ) == "1.2.4-alpha4"


def test_next_version_prerelease_switches_to_later_token():
    assert str(
        Version(1, 2, 3, "alpha.1").next_version("prerelease", "beta")
    ) == "1.2.3-beta.1"


def test_next_version_prerelease_switches_to_earlier_token():
    assert str(
        Version(1, 2, 3, "rc.1").next_version("prerelease", "alpha")
    ) == "1.2.4-alpha.1"


def test_next_version_prerelease_same_token_without_number():
    assert str(
        Version(1, 2, 3, "rc").next_version("prerelease", "rc")
    ) == "1.2.3-rc.1"


def test_next_version_prerelease_empty_token():
    assert str(Version(1, 2, 3).next_version("prerelease", "")) == (
        "1.2.4-1"
    )


def test_next_version_prerelease_none_token():
    assert str(Version(1, 2, 3).next_version("prerelease", None)) == (
        "1.2.4-rc.1"
    )


@pytest.mark.parametrize("token", ["bad_token", "bad token", "a..b"])
def test_next_version_rejects_invalid_prerelease_token(token):
    with pytest.raises(ValueError):
        Version(1, 2, 3).next_version("prerelease", token)


def test_next_version_prerelease_drops_build_metadata():
    result = Version(1, 2, 3, "rc.1", "build.5").next_version("prerelease")
    assert result.build is None


def test_next_version_patch_from_prerelease_finalizes():
    result = Version(1, 2, 3, "rc.1", "build.5").next_version("patch")
    assert result == Version(1, 2, 3)
    assert result.build is None


def test_next_version_minor_from_prerelease_with_zero_patch_finalizes():
    result = Version(1, 2, 0, "rc.1", "build.5").next_version("minor")
    assert result == Version(1, 2, 0)
    assert result.build is None


def test_next_version_major_from_prerelease_with_zero_minor_and_patch_finalizes():
    result = Version(1, 0, 0, "rc.1", "build.5").next_version("major")
    assert result == Version(1, 0, 0)
    assert result.build is None


def test_next_version_minor_from_prerelease_with_nonzero_patch_bumps_minor():
    result = Version(1, 2, 3, "rc.1").next_version("minor")
    assert result == Version(1, 3, 0)


def test_next_version_major_from_prerelease_with_nonzero_minor_bumps_major():
    result = Version(1, 2, 3, "rc.1").next_version("major")
    assert result == Version(2, 0, 0)


def test_replace_one_part():
    assert Version(1, 2, 3).replace(major=4) == Version(4, 2, 3)


def test_replace_multiple_parts():
    assert Version(1, 2, 3, "alpha", "build").replace(
        minor=4, patch=5, prerelease="beta", build="next"
    ) == Version(1, 4, 5, "beta", "next")


def test_replace_can_remove_metadata():
    assert Version(1, 2, 3, "alpha", "build").replace(
        prerelease=None, build=None
    ) == Version(1, 2, 3)


def test_replace_does_not_mutate_original():
    original = Version(1, 2, 3, "alpha", "build")
    original.replace(major=5)
    assert original == Version(1, 2, 3, "alpha", "build")


def test_replace_invalid_key():
    with pytest.raises(TypeError, match="unexpected keyword argument"):
        Version(1, 2, 3).replace(unknown=4)


def test_replace_multiple_invalid_keys():
    with pytest.raises(TypeError, match="2 unexpected keyword argument"):
        Version(1, 2, 3).replace(first=1, second=2)


def test_replace_invalid_value_propagates_type_error():
    with pytest.raises(ValueError):
        Version(1, 2, 3).replace(major="invalid")


def test_replace_negative_value_propagates_value_error():
    with pytest.raises(ValueError):
        Version(1, 2, 3).replace(major=-1)


@pytest.mark.parametrize(
    "value",
    [
        "1.2.3",
        "0.0.0",
        "1.2.3-alpha",
        "1.2.3+build",
        "1.2.3-alpha+build",
        b"1.2.3",
    ],
)
def test_is_valid_true(value):
    assert Version.is_valid(value) is True


@pytest.mark.parametrize(
    "value",
    [
        "",
        "1",
        "1.2",
        "01.2.3",
        "1.2.3-alpha_1",
        "1.2.3+build_meta",
        "invalid",
    ],
)
def test_is_valid_false(value):
    assert Version.is_valid(value) is False


def test_is_valid_propagates_type_error():
    with pytest.raises(TypeError):
        Version.is_valid(123)


@pytest.mark.parametrize(
    ("current", "other", "expected"),
    [
        ("1.0.0", "1.0.0", True),
        ("1.0.0", "1.0.1", True),
        ("1.0.0", "1.1.0", True),
        ("1.1.0", "1.0.0", False),
        ("1.0.0", "2.0.0", False),
        ("1.2.3", "1.2.0", True),
        ("1.2.3", "1.3.0", True),
        ("1.2.3-alpha", "1.3.0-alpha", True),
        ("1.2.3-alpha", "1.3.0-beta", False),
        ("0.0.0", "0.0.0", True),
        ("0.0.0", "0.0.1", False),
        ("0.1.0", "0.2.0", False),
        ("0.1.0-alpha", "0.1.0-alpha", True),
    ],
)
def test_is_compatible(current, other, expected):
    assert Version.parse(current).is_compatible(Version.parse(other)) is expected


@pytest.mark.parametrize("other", ["1.2.3", (1, 2, 3), None, 123])
def test_is_compatible_rejects_non_version(other):
    with pytest.raises(TypeError, match="Expected a Version type"):
        Version(1, 2, 3).is_compatible(other)


def test_is_compatible_ignores_patch_for_positive_major():
    assert Version(1, 2, 1).is_compatible(Version(1, 2, 99)) is True


def test_is_compatible_requires_same_prerelease():
    assert Version(1, 2, 3, "alpha").is_compatible(
        Version(1, 2, 4, "beta")
    ) is False


def test_is_compatible_major_zero_requires_equal_first_four_parts():
    assert Version(0, 1, 0, "alpha").is_compatible(
        Version(0, 1, 0, "alpha", "build.1")
    ) is True
    assert Version(0, 1, 0, "alpha").is_compatible(
        Version(0, 1, 0, "beta")
    ) is False


def test_is_compatible_major_zero_with_different_patch():
    assert Version(0, 1, 0).is_compatible(Version(0, 1, 1)) is False


def test_bump_methods_and_finalize_return_new_objects():
    original = Version(1, 2, 3, "alpha", "build")
    results = [
        original.bump_major(),
        original.bump_minor(),
        original.bump_patch(),
        original.bump_prerelease(),
        original.bump_build(),
        original.finalize_version(),
    ]
    assert all(result is not original for result in results)
    assert original.to_tuple() == (1, 2, 3, "alpha", "build")


def test_comparison_sorting():
    versions = [
        Version.parse("1.0.0"),
        Version.parse("1.0.0-alpha.2"),
        Version.parse("1.0.0-alpha.10"),
        Version.parse("1.0.0-alpha"),
        Version.parse("2.0.0"),
    ]
    assert [str(item) for item in sorted(versions)] == [
        "1.0.0-alpha",
        "1.0.0-alpha.2",
        "1.0.0-alpha.10",
        "1.0.0",
        "2.0.0",
    ]


def test_build_metadata_does_not_affect_equality():
    assert Version.parse("1.2.3+one") == Version.parse("1.2.3+two")


def test_build_metadata_does_not_affect_ordering():
    assert not Version.parse("1.2.3+one") < Version.parse("1.2.3+two")
    assert not Version.parse("1.2.3+one") > Version.parse("1.2.3+two")


def test_comparison_with_dict_using_prerelease():
    assert Version(1, 2, 3, "alpha") < {
        "major": 1,
        "minor": 2,
        "patch": 3,
    }


def test_comparison_with_tuple_containing_metadata():
    assert Version(1, 2, 3, "alpha") < (1, 2, 3, "beta")


def test_parse_arbitrarily_large_numeric_components():
    major = "9" * 100
    result = Version.parse(f"{major}.0.0")
    assert result.major == int(major)


def test_parse_arbitrarily_large_prerelease_numeric_identifier():
    identifier = "9" * 500
    result = Version.parse(f"1.2.3-alpha.{identifier}")
    assert result.prerelease == f"alpha.{identifier}"


def test_nat_cmp_large_ascii_numbers_without_integer_conversion():
    left = "alpha." + "9" * 500
    right = "alpha." + "1" + "0" * 500
    assert Version._nat_cmp(left, right) == -1


def test_nat_cmp_leading_zero_numeric_identifiers():
    assert Version._nat_cmp("alpha.0002", "alpha.2") == 0


def test_nat_cmp_numeric_and_non_numeric_identifiers():
    assert Version._nat_cmp("alpha.2", "alpha.a") == -1
    assert Version._nat_cmp("alpha.a", "alpha.2") == 1


def test_parse_rejects_leading_zero_prerelease_numeric_identifier():
    with pytest.raises(ValueError):
        Version.parse("1.2.3-alpha.01")


def test_parse_accepts_zero_prerelease_identifier():
    assert Version.parse("1.2.3-alpha.0").prerelease == "alpha.0"


def test_parse_accepts_hyphens_in_prerelease_and_build():
    result = Version.parse("1.2.3-alpha-beta+build-meta")
    assert result.prerelease == "alpha-beta"
    assert result.build == "build-meta"


def test_parse_rejects_non_ascii_identifiers():
    with pytest.raises(ValueError):
        Version.parse("1.2.3-álpha")


def test_parse_rejects_unicode_digits_in_version_numbers():
    with pytest.raises(ValueError):
        Version.parse("١.2.3")


def test_compare_prerelease_numeric_identifiers_with_leading_zero_constructor_values():
    assert Version(1, 0, 0, "alpha.02").compare(
        Version(1, 0, 0, "alpha.2")
    ) == 0


def test_comparator_handles_invalid_collection_operands():
    instance = Version(1, 2, 3)
    assert Version.__eq__(instance, (1, 2, 3, 4, 5, 6)) is NotImplemented
    assert Version.__lt__(instance, {"unknown": 1}) is NotImplemented
    assert Version.__gt__(instance, [1, 2, 3, 4, 5, 6]) is NotImplemented


def test_replace_preserves_subclass():
    class CustomVersion(Version):
        pass

    result = CustomVersion(1, 2, 3).replace(minor=4)
    assert isinstance(result, CustomVersion)


def test_finalize_preserves_subclass():
    class CustomVersion(Version):
        pass

    result = CustomVersion(1, 2, 3, "alpha", "build").finalize_version()
    assert isinstance(result, CustomVersion)


def test_bump_prerelease_preserves_subclass():
    class CustomVersion(Version):
        pass

    result = CustomVersion(1, 2, 3).bump_prerelease()
    assert isinstance(result, CustomVersion)


def test_bump_build_preserves_subclass():
    class CustomVersion(Version):
        pass

    result = CustomVersion(1, 2, 3).bump_build()
    assert isinstance(result, CustomVersion)


def test_next_version_preserves_subclass():
    class CustomVersion(Version):
        pass

    result = CustomVersion(1, 2, 3).next_version("patch")
    assert isinstance(result, CustomVersion)
