import pickle
import pytest
from packaging.version import (
    Version,
    InvalidVersion,
    normalize_pre,
    parse,
    __dir__,
)


def test_dir():
    assert "Version" in __dir__()
    assert "parse" in __dir__()


def test_normalize_pre():
    assert normalize_pre("alpha") == "a"
    assert normalize_pre("BETA") == "b"
    assert normalize_pre("rc") == "rc"
    assert normalize_pre("preview") == "rc"
    assert normalize_pre("pre") == "rc"
    assert normalize_pre("c") == "rc"
    assert normalize_pre("rev") == "post"
    assert normalize_pre("r") == "post"
    assert normalize_pre("unknown") == "unknown"


def test_parse():
    v = parse("1.0.dev1")
    assert isinstance(v, Version)
    assert str(v) == "1.0.dev1"


def test_version_simple_parsing():
    v = Version("1.2.3")
    assert v.release == (1, 2, 3)
    assert v.epoch == 0
    assert v.pre is None
    assert v.post is None
    assert v.dev is None
    assert v.local is None


def test_version_complex_parsing():
    v = Version("1!2.3.4a1.post2.dev3+local.1")
    assert v.epoch == 1
    assert v.release == (2, 3, 4)
    assert v.pre == ("a", 1)
    assert v.post == 2
    assert v.dev == 3
    assert v.local == "local.1"
    assert v.public == "1!2.3.4.a1.post2.dev3"
    assert v.base_version == "1!2.3.4"
    assert v.is_prerelease is True


def test_invalid_versions():
    with pytest.raises(InvalidVersion):
        Version("invalid")
    with pytest.raises(InvalidVersion):
        Version("1..2")
    with pytest.raises(InvalidVersion):
        Version(None)  # type: ignore
    with pytest.raises(InvalidVersion):
        Version(123)  # type: ignore


def test_from_parts():
    v = Version.from_parts(release=(1, 2, 3), pre=("alpha", 1), post=2, dev=1, local="abc", epoch=1)
    assert v.epoch == 1
    assert v.release == (1, 2, 3)
    assert v.pre == ("a", 1)
    assert v.post == 2
    assert v.dev == 1
    assert v.local == "abc"


def test_from_parts_validation_errors():
    with pytest.raises(InvalidVersion):
        Version.from_parts(release=(1,), epoch=-1)
    with pytest.raises(InvalidVersion):
        Version.from_parts(release=())
    with pytest.raises(InvalidVersion):
        Version.from_parts(release=(1,), pre=("invalid", 1))
    with pytest.raises(InvalidVersion):
        Version.from_parts(release=(1,), post=-1)
    with pytest.raises(InvalidVersion):
        Version.from_parts(release=(1,), dev=-1)
    with pytest.raises(InvalidVersion):
        Version.from_parts(release=(1,), local="INVALID LOCAL!")


def test_replace():
    v = Version("1.2.3")
    v2 = v.__replace__(pre=("beta", 2), epoch=2, local="test")
    assert v2.epoch == 2
    assert v2.release == (1, 2, 3)
    assert v2.pre == ("b", 2)
    assert v2.local == "test"

    # Test identical replace returns self
    assert v.__replace__() is v


def test_version_comparisons():
    v1 = Version("1.0a5")
    v2 = Version("1.0")

    assert v1 < v2
    assert v1 <= v2
    assert v1 != v2
    assert v2 > v1
    assert v2 >= v1
    assert v1 == Version("1.0a5")

    # Comparison with non-Version objects
    assert (v1 < "1.0") is NotImplemented  # type: ignore
    assert (v1 <= "1.0") is NotImplemented  # type: ignore
    assert (v1 == "1.0") is False
    assert (v1 != "1.0") is True
    assert (v1 > "1.0") is NotImplemented  # type: ignore
    assert (v1 >= "1.0") is NotImplemented  # type: ignore


def test_version_hash():
    v1 = Version("1.2.3")
    v2 = Version("1.2.3")
    assert hash(v1) == hash(v2)
    assert v1 in {v1}


def test_pickle_roundtrip():
    v = Version("1!2.3.4a1+local")
    dumped = pickle.dumps(v)
    loaded = pickle.loads(dumped)
    assert loaded == v
    assert loaded.epoch == v.epoch
    assert loaded.release == v.release
    assert loaded.pre == v.pre
    assert loaded.local == v.local


def test_setstate_compatibility_formats():
    v = Version("1.2.3")

    # Test old slot dict format (26.0-26.1)
    v.__setstate__(
        (None, {"_epoch": 0, "_release": (1, 2, 3), "_pre": None, "_post": None, "_dev": None, "_local": None}))
    assert v.release == (1, 2, 3)

    # Test very old dict format
    class DummyVersion:
        epoch = 0
        release = (1, 2, 3)
        dev = None
        pre = None
        post = None
        local = None

    v.__setstate__({"_version": DummyVersion()})
    assert v.release == (1, 2, 3)

    # Test invalid state
    with pytest.raises(TypeError):
        v.__setstate__("invalid_state")  # type: ignore


def test_deprecated_version_property():
    v = Version("1.2.3")
    with pytest.deprecated_call():
        internal = v._version
    assert internal.release == (1, 2, 3)

    with pytest.deprecated_call():
        v._version = internal  # type: ignore
    assert v.release == (1, 2, 3)


def test_repr_and_str():
    v = Version("1.2.3a1")
    assert str(v) == "1.2.3a1"
    assert repr(v) == "<Version('1.2.3a1')>"


def test_is_prerelease_property():
    assert Version("1.2.3").is_prerelease is False
    assert Version("1.2.3a1").is_prerelease is True