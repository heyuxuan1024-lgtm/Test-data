
import pytest
from semver import version


def test_constructor_defaults_and_properties():
    v = version.Version(1)
    assert v.major == 1
    assert v.minor == 0
    assert v.patch == 0
    assert v.prerelease is None
    assert v.build is None
    assert v.to_tuple() == (1, 0, 0, None, None)
    assert v.to_dict() == {
        "major": 1,
        "minor": 0,
        "patch": 0,
        "prerelease": None,
        "build": None,
    }


def test_constructor_all_parts_and_type_conversion():
    v = version.Version("1", "2", "3", 4, 5)
    assert v.to_tuple() == (1, 2, 3, "4", "5")


@pytest.mark.parametrize("part", ["major", "minor", "patch"])
def test_constructor_rejects_negative_numeric_parts(part):
    values = {"major": 1, "minor": 2, "patch": 3}
    values[part] = -1
    with pytest.raises(ValueError):
        version.Version(**values)


@pytest.mark.parametrize(
    "args",
    [
        ("not-a-number",),
        (1, "invalid"),
        (1, 2, "invalid"),
        (None,),
        (1, None),
    ],
)
def test_constructor_rejects_non_integer_convertible_parts(args):
    with pytest.raises((TypeError, ValueError)):
        version.Version(*args)


@pytest.mark.parametrize(
    "part,value",
    [
        ("major", 2),
        ("minor", 2),
        ("patch", 2),
        ("prerelease", "alpha"),
        ("build", "build"),
    ],
)
def test_properties_are_read_only(part, value):
    v = version.Version(1, 2, 3, "alpha", "build")
    with pytest.raises(AttributeError):
        setattr(v, part, value)


def test_names_and_slots():
    assert version.Version.NAMES == (
        "major",
        "minor",
        "patch",
        "prerelease",
        "build",
    )
    assert version.Version.__slots__ == (
        "_major",
        "_minor",
        "_patch",
        "_prerelease",
        "_build",
    )
    with pytest.raises(AttributeError):
        version.Version(1).extra = 1


def test_to_tuple_to_dict_and_iteration():
    v = version.Version(1, 2, 3, "alpha.1", "build.5")
    expected = (1, 2, 3, "alpha.1", "build.5")
    assert v.to_tuple() == expected
    assert tuple(v) == expected
    assert list(v) == list(expected)
    assert v.to_dict() == dict(
        major=1,
        minor=2,
        patch=3,
        prerelease="alpha.1",
        build="build.5",
    )


@pytest.mark.parametrize(
    "value,expected",
    [
        ("1.2.3", (1, 2, 3, None, None)),
        ("0.0.0", (0, 0, 0, None, None)),
        ("1.2.3-alpha", (1, 2, 3, "alpha", None)),
        ("1.2.3+build", (1, 2, 3, None, "build")),
        ("1.2.3-alpha.1+build.5", (1, 2, 3, "alpha.1", "build.5")),
        ("1.2.3-0", (1, 2, 3, "0", None)),
        ("1.2.3-01", (1, 2, 3, "01", None)),
        ("1.2.3-rc.1+001", (1, 2, 3, "rc.1", "001")),
    ],
)
def test_parse_valid_versions(value, expected):
    assert version.Version.parse(value).to_tuple() == expected


@pytest.mark.parametrize(
    "value",
    [
        "1",
        "1.2",
        "01.2.3",
        "1.02.3",
        "1.2.03",
        "1.2.3-",
        "1.2.3+",
        "1.2.3-alpha..1",
        "1.2.3+build..1",
        "1.2.3-alpha_1",
        "1.2.3+build_1",
        "1.2.3-@",
        "1.2.3+@",
        "",
        " ",
        "v1.2.3",
        "1.2.3 ",
        " 1.2.3",
        "1.2.3\n",
        "1.2.3.4",
    ],
)
def test_parse_rejects_invalid_versions(value):
    with pytest.raises(ValueError):
        version.Version.parse(value)


@pytest.mark.parametrize(
    "value,expected",
    [
        ("1", (1, 0, 0, None, None)),
        ("1.2", (1, 2, 0, None, None)),
        ("1.2.3", (1, 2, 3, None, None)),
        ("1-alpha", (1, 0, 0, "alpha", None)),
        ("1.2-alpha", (1, 2, 0, "alpha", None)),
        ("1+build", (1, 0, 0, None, "build")),
        ("1.2+build", (1, 2, 0, None, "build")),
    ],
)
def test_parse_optional_minor_and_patch(value, expected):
    assert version.Version.parse(
        value, optional_minor_and_patch=True
    ).to_tuple() == expected


@pytest.mark.parametrize("value", ["1", "1.2"])
def test_parse_requires_optional_flag_for_short_versions(value):
    with pytest.raises(ValueError):
        version.Version.parse(value)


def test_parse_bytes():
    assert version.Version.parse(b"1.2.3-alpha+build").to_tuple() == (
        1,
        2,
        3,
        "alpha",
        "build",
    )


@pytest.mark.parametrize("value", [None, 1, 1.2, [], {}, object()])
def test_parse_rejects_wrong_types(value):
    with pytest.raises(TypeError):
        version.Version.parse(value)


def test_parse_invalid_utf8_bytes():
    with pytest.raises(UnicodeDecodeError):
        version.Version.parse(b"\xff")


def test_parse_supports_arbitrarily_large_numbers():
    number = 10**100
    parsed = version.Version.parse(f"{number}.0.0")
    assert parsed.major == number


def test_is_valid():
    assert version.Version.is_valid("1.2.3")
    assert version.Version.is_valid(b"1.2.3")
    assert not version.Version.is_valid("01.2.3")
    assert not version.Version.is_valid("invalid")


def test_is_valid_propagates_type_errors():
    with pytest.raises(TypeError):
        version.Version.is_valid(None)


def test_validate_identifiers_accepts_valid_values():
    version.Version._validate_identifiers(
        "alpha.1-beta", version.Version._PRERELEASE_IDENTIFIER, "prerelease"
    )
    version.Version._validate_identifiers(
        "build.1-beta", version.Version._BUILD_IDENTIFIER, "build"
    )


@pytest.mark.parametrize(
    "value,pattern",
    [
        ("", version.Version._PRERELEASE_IDENTIFIER),
        ("alpha..beta", version.Version._PRERELEASE_IDENTIFIER),
        ("01", version.Version._PRERELEASE_IDENTIFIER),
        ("alpha_1", version.Version._PRERELEASE_IDENTIFIER),
        ("build..1", version.Version._BUILD_IDENTIFIER),
        ("build_1", version.Version._BUILD_IDENTIFIER),
        ("build!", version.Version._BUILD_IDENTIFIER),
    ],
)
def test_validate_identifiers_rejects_invalid_values(value, pattern):
    with pytest.raises(ValueError):
        version.Version._validate_identifiers(value, pattern, "identifier")


@pytest.mark.parametrize(
    "a,b,expected",
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
        ("10", "2", 1),
        ("2", "10", -1),
        ("1alpha", "2", 1),
    ],
)
def test_natural_prerelease_comparison(a, b, expected):
    assert version.Version._nat_cmp(a, b) == expected


def test_natural_prerelease_comparison_handles_leading_zeroes():
    assert version.Version._nat_cmp("01", "1") == 0
    assert version.Version._nat_cmp("0002", "2") == 0
    assert version.Version._nat_cmp("00010", "2") == 1


def test_natural_prerelease_comparison_handles_non_ascii_digits():
    assert version.Version._nat_cmp("١", "1") == 0
    assert version.Version._nat_cmp("٢", "1") == 1


def test_increment_prerelease_numeric_suffix():
    assert version.Version._increment_prerelease("rc.1") == "rc.2"
    assert version.Version._increment_prerelease("alpha.9") == "alpha.10"
    assert version.Version._increment_prerelease("9") == "10"


def test_increment_prerelease_without_numeric_suffix():
    assert version.Version._increment_prerelease("alpha") == "alpha.0"
    assert version.Version._increment_prerelease("alpha.beta") == "alpha.beta.0"


def test_increment_string_numeric_suffix():
    assert version.Version._increment_string("build.1") == "build.2"
    assert version.Version._increment_string("build.9") == "build.10"
    assert version.Version._increment_string("a99b") == "a100b"


def test_increment_string_without_digits():
    assert version.Version._increment_string("build") == "build"
    assert version.Version._increment_string("") == ""


def test_bump_major():
    original = version.Version(1, 2, 3, "alpha", "build")
    bumped = original.bump_major()
    assert bumped.to_tuple() == (2, 0, 0, None, None)
    assert original.to_tuple() == (1, 2, 3, "alpha", "build")


def test_bump_minor():
    original = version.Version(1, 2, 3, "alpha", "build")
    bumped = original.bump_minor()
    assert bumped.to_tuple() == (1, 3, 0, None, None)
    assert original.to_tuple() == (1, 2, 3, "alpha", "build")


def test_bump_patch():
    original = version.Version(1, 2, 3, "alpha", "build")
    bumped = original.bump_patch()
    assert bumped.to_tuple() == (1, 2, 4, None, None)
    assert original.to_tuple() == (1, 2, 3, "alpha", "build")


@pytest.mark.parametrize(
    "prerelease,token,bump_when_empty,expected",
    [
        (None, "rc", False, (1, 2, 3, "rc.1", None)),
        (None, "", False, (1, 2, 3, "1", None)),
        (None, None, False, (1, 2, 3, "rc.1", None)),
        ("rc.1", "rc", False, (1, 2, 3, "rc.2", None)),
        ("alpha", "rc", False, (1, 2, 3, "alpha.0", None)),
        ("alpha.9", "rc", False, (1, 2, 3, "alpha.10", None)),
        (None, "rc", True, (1, 2, 4, "rc.1", None)),
    ],
)
def test_bump_prerelease(prerelease, token, bump_when_empty, expected):
    v = version.Version(1, 2, 3, prerelease, "old")
    bumped = v.bump_prerelease(token, bump_when_empty)
    assert bumped.to_tuple() == expected
    assert v.to_tuple() == (1, 2, 3, prerelease, "old")


@pytest.mark.parametrize("token", ["bad_token", "bad.token!", ""])
def test_bump_prerelease_invalid_tokens(token):
    if token == "":
        return
    with pytest.raises(ValueError):
        version.Version(1).bump_prerelease(token)


def test_bump_prerelease_numeric_token():
    assert str(version.Version(1).bump_prerelease("1")) == "1.0.0-1.1"


@pytest.mark.parametrize(
    "build,token,expected",
    [
        (None, "build", "build.0"),
        (None, "", "0"),
        (None, None, "build.0"),
        ("build.1", "other", "build.2"),
        ("build.9", "other", "build.10"),
        ("alpha", "other", "alpha.0"),
        ("alpha.9", "other", "alpha.10"),
    ],
)
def test_bump_build(build, token, expected):
    v = version.Version(1, 2, 3, "rc", build)
    bumped = v.bump_build(token)
    assert bumped.build == expected
    assert v.build == build
    assert bumped.prerelease == "rc"


@pytest.mark.parametrize("token", ["bad_token", "bad.token!"])
def test_bump_build_invalid_tokens(token):
    with pytest.raises(ValueError):
        version.Version(1).bump_build(token)


def test_bump_build_large_numeric_suffix():
    assert version.Version(1, build="build.999999999999999999999").bump_build().build == (
        "build.1000000000000000000000"
    )


@pytest.mark.parametrize(
    "left,right,expected",
    [
        ("1.0.0", "2.0.0", -1),
        ("2.0.0", "1.0.0", 1),
        ("1.0.0", "1.0.0", 0),
        ("1.0.0-alpha", "1.0.0", -1),
        ("1.0.0", "1.0.0-alpha", 1),
        ("1.0.0-alpha.1", "1.0.0-alpha.2", -1),
        ("1.0.0-alpha", "1.0.0-beta", -1),
        ("1.0.0+build.1", "1.0.0+build.2", 0),
        ("1.0.0-alpha+one", "1.0.0-alpha+two", 0),
    ],
)
def test_compare_versions(left, right, expected):
    assert version.Version.parse(left).compare(version.Version.parse(right)) == expected


@pytest.mark.parametrize(
    "other",
    [
        "2.0.0",
        b"2.0.0",
        {"major": 2},
        (2,),
        [2, 0, 0],
        version.Version(2),
    ],
)
def test_compare_supported_operand_types(other):
    assert version.Version(1).compare(other) == -1


@pytest.mark.parametrize("other", [None, 1, 1.2, object(), set()])
def test_compare_rejects_unsupported_operand_types(other):
    with pytest.raises(TypeError):
        version.Version(1).compare(other)


@pytest.mark.parametrize(
    "other",
    [
        {},
        {"unknown": 1},
        (),
        (1, 2, 3, 4, 5, 6),
        (1, -1),
        [1, "invalid"],
    ],
)
def test_compare_invalid_collections_raise_conversion_errors(other):
    with pytest.raises((TypeError, ValueError)):
        version.Version(1).compare(other)


def test_compare_dictionary_and_sequence_equivalence():
    v = version.Version(1, 2, 3, "alpha", "build")
    assert v.compare(
        {
            "major": 1,
            "minor": 2,
            "patch": 3,
            "prerelease": "alpha",
            "build": "other",
        }
    ) == 0
    assert v.compare((1, 2, 3, "alpha", "other")) == 0


@pytest.mark.parametrize(
    "left,right",
    [
        ("1.0.0", "2.0.0"),
        ("1.0.0-alpha", "1.0.0"),
        ("1.0.0-alpha.1", "1.0.0-alpha.2"),
    ],
)
def test_comparison_operators(left, right):
    a = version.Version.parse(left)
    b = version.Version.parse(right)
    assert a < b
    assert a <= b
    assert b > a
    assert b >= a
    assert a != b
    assert not a == b


def test_comparison_operators_with_supported_operand_types():
    v = version.Version(1, 2, 3)
    assert v == "1.2.3"
    assert v == (1, 2, 3)
    assert v == [1, 2, 3]
    assert v == {"major": 1, "minor": 2, "patch": 3}
    assert v != "1.2.4"
    assert v < "1.2.4"
    assert v <= "1.2.3"
    assert v > "1.2.2"
    assert v >= "1.2.3"


@pytest.mark.parametrize("other", [None, 1, 1.2, object(), set()])
def test_comparison_operators_return_not_implemented_for_unsupported_types(other):
    v = version.Version(1, 2, 3)
    assert v.__eq__(other) is NotImplemented
    assert v.__ne__(other) is NotImplemented
    assert v.__lt__(other) is NotImplemented
    assert v.__le__(other) is NotImplemented
    assert v.__gt__(other) is NotImplemented
    assert v.__ge__(other) is NotImplemented


@pytest.mark.parametrize(
    "other",
    [
        {},
        {"unknown": 1},
        (),
        (1, 2, 3, 4, 5, 6),
        (1, -1),
        [1, "invalid"],
    ],
)
def test_comparison_operators_return_not_implemented_for_invalid_collections(other):
    v = version.Version(1)
    assert v.__eq__(other) is NotImplemented
    assert v.__ne__(other) is NotImplemented
    assert v.__lt__(other) is NotImplemented
    assert v.__le__(other) is NotImplemented
    assert v.__gt__(other) is NotImplemented
    assert v.__ge__(other) is NotImplemented


def test_getitem_integer_indices():
    v = version.Version(1, 2, 3, "alpha", "build")
    assert v[0] == 1
    assert v[1] == 2
    assert v[2] == 3
    assert v[3] == "alpha"
    assert v[4] == "build"


def test_getitem_slices():
    v = version.Version(1, 2, 3, "alpha", "build")
    assert v[:3] == (1, 2, 3)
    assert v[1:4] == (2, 3, "alpha")
    assert v[::2] == (1, 3, "build")
    assert v[1:5:2] == (2, "alpha")
    assert v[2:2] == ()


def test_getitem_omits_undefined_parts():
    v = version.Version(1, 2, 3)
    assert v[0:5] == (1, 2, 3)
    assert v[3:5] == ()


def test_getitem_undefined_single_part_raises():
    v = version.Version(1, 2, 3)
    with pytest.raises(IndexError):
        _ = v[3]
    with pytest.raises(IndexError):
        _ = v[4]


@pytest.mark.parametrize("index", [-1, -2, -5, slice(-1, 3), slice(0, -1)])
def test_getitem_rejects_negative_indices(index):
    with pytest.raises(IndexError):
        _ = version.Version(1, 2, 3)[index]


@pytest.mark.parametrize("index", [5, 100])
def test_getitem_out_of_range(index):
    with pytest.raises(IndexError):
        _ = version.Version(1, 2, 3)[index]


def test_getitem_supports_index_protocol():
    class IndexValue:
        def __index__(self):
            return 1

    assert version.Version(1, 2, 3)[IndexValue()] == 2


def test_getitem_rejects_invalid_index_type():
    with pytest.raises(TypeError):
        _ = version.Version(1, 2, 3)["1"]


def test_getitem_invalid_slice_index_type():
    with pytest.raises(TypeError):
        _ = version.Version(1, 2, 3)["1":3]


def test_repr_and_str():
    v = version.Version(1, 2, 3, "alpha.1", "build.5")
    assert str(v) == "1.2.3-alpha.1+build.5"
    assert repr(v) == (
        "Version(major=1, minor=2, patch=3, "
        "prerelease='alpha.1', build='build.5')"
    )


@pytest.mark.parametrize(
    "v,expected",
    [
        (version.Version(1), "1.0.0"),
        (version.Version(1, 2), "1.2.0"),
        (version.Version(1, 2, 3, ""), "1.2.3"),
        (version.Version(1, 2, 3, None, ""), "1.2.3"),
        (version.Version(1, 2, 3, "alpha"), "1.2.3-alpha"),
        (version.Version(1, 2, 3, None, "build"), "1.2.3+build"),
    ],
)
def test_string_representation(v, expected):
    assert str(v) == expected


def test_hash_ignores_build_metadata():
    first = version.Version(1, 2, 3, "alpha", "one")
    second = version.Version(1, 2, 3, "alpha", "two")
    assert first == second
    assert hash(first) == hash(second)


def test_hash_includes_prerelease():
    first = version.Version(1, 2, 3, "alpha")
    second = version.Version(1, 2, 3, "beta")
    assert hash(first) != hash(second)


def test_hash_supports_dictionary_keys_and_sets():
    first = version.Version(1, 2, 3, build="one")
    second = version.Version(1, 2, 3, build="two")
    assert {first: "value"}[second] == "value"
    assert len({first, second}) == 1


def test_finalize_version():
    original = version.Version(1, 2, 3, "alpha", "build")
    finalized = original.finalize_version()
    assert finalized.to_tuple() == (1, 2, 3, None, None)
    assert original.to_tuple() == (1, 2, 3, "alpha", "build")


@pytest.mark.parametrize(
    "expression,expected",
    [
        (">1.0.0", True),
        ("<2.0.0", True),
        (">=1.0.0", True),
        ("<=1.0.0", True),
        ("==1.0.0", True),
        ("!=2.0.0", True),
        ("1.0.0", True),
        ("1.0.1", False),
        ("<1.0.0", False),
        (">1.0.0", False),
        ("<=0.9.9", False),
        (">=1.0.1", False),
        ("!=1.0.0", False),
    ],
)
def test_match(expression, expected):
    assert version.Version.parse("1.0.0").match(expression) is expected


@pytest.mark.parametrize(
    "expression",
    ["", "abc", "==", "!=", "=>1.0.0", "~1.0.0", "^1.0.0", " 1.0.0"],
)
def test_match_invalid_expression(expression):
    with pytest.raises((ValueError, KeyError)):
        version.Version(1).match(expression)


def test_match_invalid_version_expression():
    with pytest.raises(ValueError):
        version.Version(1).match(">=invalid")


@pytest.mark.parametrize(
    "part,expected",
    [
        ("major", "2.0.0"),
        ("minor", "1.3.0"),
        ("patch", "1.2.4"),
        ("prerelease", "1.2.4-rc.1"),
    ],
)
def test_next_version(part, expected):
    assert str(version.Version(1, 2, 3).next_version(part)) == expected


@pytest.mark.parametrize(
    "part,expected",
    [
        ("major", "2.0.0"),
        ("minor", "1.3.0"),
        ("patch", "1.2.4"),
    ],
)
def test_next_version_clears_existing_prerelease_and_build(part, expected):
    v = version.Version(1, 2, 3, "alpha.1", "build.1")
    assert str(v.next_version(part)) == expected


def test_next_version_clears_prerelease_for_zero_patch_minor():
    assert str(version.Version(1, 2, 0, "alpha").next_version("minor")) == "1.2.0"
    assert str(version.Version(1, 0, 0, "alpha").next_version("major")) == "1.0.0"


def test_next_version_preserves_progress_for_prerelease():
    assert str(version.Version.parse("1.2.3-rc.1").next_version("prerelease")) == (
        "1.2.3-rc.2"
    )
    assert str(version.Version.parse("1.2.3-rc9").next_version("prerelease")) == (
        "1.2.3-rc10"
    )


def test_next_version_advances_patch_for_earlier_prerelease_token():
    result = version.Version.parse("1.2.3-rc.1").next_version(
        "prerelease", "alpha"
    )
    assert str(result) == "1.2.4-alpha.1"


def test_next_version_switches_to_later_prerelease_token_without_patch():
    result = version.Version.parse("1.2.3-alpha.1").next_version(
        "prerelease", "rc"
    )
    assert str(result) == "1.2.3-rc.1"


def test_next_version_old_style_counter_advances_patch_when_needed():
    result = version.Version.parse("1.2.3-rc9").next_version(
        "prerelease", "rc"
    )
    assert str(result) == "1.2.3-rc10"


def test_next_version_nonmatching_prerelease_token():
    result = version.Version.parse("1.2.3-beta.1").next_version(
        "prerelease", "rc"
    )
    assert str(result) == "1.2.4-rc.1"


def test_next_version_empty_prerelease_token():
    result = version.Version.parse("1.2.3").next_version("prerelease", "")
    assert str(result) == "1.2.4-rc.1"


@pytest.mark.parametrize("part", ["build", "invalid", "", None])
def test_next_version_rejects_invalid_parts(part):
    with pytest.raises(ValueError):
        version.Version(1).next_version(part)


@pytest.mark.parametrize("token", ["bad_token", "bad.token!"])
def test_next_version_rejects_invalid_prerelease_token(token):
    with pytest.raises(ValueError):
        version.Version.parse("1.2.3-alpha").next_version(
            "prerelease", token
        )


def test_replace_one_part():
    v = version.Version(1, 2, 3, "alpha", "build")
    result = v.replace(major=4)
    assert result.to_tuple() == (4, 2, 3, "alpha", "build")
    assert v.to_tuple() == (1, 2, 3, "alpha", "build")


def test_replace_multiple_parts():
    v = version.Version(1, 2, 3, "alpha", "build")
    result = v.replace(minor=5, patch=6, prerelease="beta", build="new")
    assert result.to_tuple() == (1, 5, 6, "beta", "new")


def test_replace_can_clear_metadata():
    v = version.Version(1, 2, 3, "alpha", "build")
    result = v.replace(prerelease=None, build=None)
    assert result.to_tuple() == (1, 2, 3, None, None)


def test_replace_rejects_unknown_keyword():
    with pytest.raises(TypeError, match="unexpected keyword"):
        version.Version(1).replace(unknown=1)


def test_replace_propagates_invalid_part_errors():
    with pytest.raises(ValueError):
        version.Version(1).replace(major=-1)


def test_replace_propagates_constructor_type_errors():
    with pytest.raises((TypeError, ValueError)):
        version.Version(1).replace(major="invalid")


def test_is_compatible_equal_versions():
    assert version.Version(1, 2, 3).is_compatible(version.Version(1, 2, 3))


def test_is_compatible_ignores_patch():
    assert version.Version(1, 2, 3).is_compatible(version.Version(1, 2, 9))
    assert version.Version(1, 2, 9).is_compatible(version.Version(1, 2, 3))


def test_is_compatible_allows_higher_minor():
    assert version.Version(1, 2, 3).is_compatible(version.Version(1, 3, 0))
    assert version.Version(1, 0, 0).is_compatible(version.Version(1, 1, 0))


def test_is_compatible_rejects_lower_minor():
    assert not version.Version(1, 2, 0).is_compatible(version.Version(1, 1, 0))


def test_is_compatible_requires_same_major():
    assert not version.Version(1, 0, 0).is_compatible(version.Version(2, 0, 0))


def test_is_compatible_requires_same_prerelease():
    assert not version.Version(1, 2, 3, "alpha").is_compatible(
        version.Version(1, 2, 3, "beta")
    )
    assert version.Version(1, 2, 3, "alpha").is_compatible(
        version.Version(1, 3, 0, "alpha")
    )


def test_is_compatible_zero_major_only_equal_first_four_parts():
    assert version.Version(0, 1, 0).is_compatible(version.Version(0, 1, 0))
    assert not version.Version(0, 1, 0).is_compatible(version.Version(0, 1, 1))
    assert not version.Version(0, 1, 0, "alpha").is_compatible(
        version.Version(0, 1, 0)
    )


@pytest.mark.parametrize("other", [None, "1.2.3", (1, 2, 3), {}, 1])
def test_is_compatible_rejects_non_version_operands(other):
    with pytest.raises(TypeError):
        version.Version(1).is_compatible(other)


def test_version_info_alias():
    assert version.VersionInfo is version.Version


def test_custom_subclass_is_preserved_by_class_methods():
    class CustomVersion(version.Version):
        pass

    parsed = CustomVersion.parse("1.2.3")
    assert type(parsed) is CustomVersion
    assert type(parsed.bump_major()) is CustomVersion
    assert type(parsed.bump_minor()) is CustomVersion
    assert type(parsed.bump_patch()) is CustomVersion
    assert type(parsed.replace(patch=4)) is CustomVersion
    assert type(parsed.finalize_version()) is CustomVersion


def test_custom_subclass_is_preserved_by_next_version():
    class CustomVersion(version.Version):
        pass

    parsed = CustomVersion.parse("1.2.3")
    assert type(parsed.next_version("patch")) is CustomVersion


def test_comparison_with_subclass():
    class CustomVersion(version.Version):
        pass

    base = version.Version(1, 2, 3)
    child = CustomVersion(1, 2, 3)
    assert base == child
    assert child == base
    assert base.compare(child) == 0
