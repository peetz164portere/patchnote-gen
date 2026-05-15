"""Tests for patchnote_gen.version_tagger."""

import pytest
from unittest.mock import patch, MagicMock
from patchnote_gen.version_tagger import (
    Version,
    parse_version,
    get_latest_tag,
    suggest_next_version,
)


# --- Version dataclass ---

def test_version_str_no_pre():
    assert str(Version(1, 2, 3)) == "1.2.3"


def test_version_str_with_pre():
    assert str(Version(1, 2, 3, "alpha.1")) == "1.2.3-alpha.1"


def test_bump_major():
    v = Version(1, 4, 9).bump_major()
    assert v == Version(2, 0, 0)


def test_bump_minor():
    v = Version(1, 4, 9).bump_minor()
    assert v == Version(1, 5, 0)


def test_bump_patch():
    v = Version(1, 4, 9).bump_patch()
    assert v == Version(1, 4, 10)


# --- parse_version ---

@pytest.mark.parametrize("tag,expected", [
    ("1.2.3", Version(1, 2, 3)),
    ("v1.2.3", Version(1, 2, 3)),
    ("0.0.1", Version(0, 0, 1)),
    ("2.10.0-beta.2", Version(2, 10, 0, "beta.2")),
    ("v3.0.0-rc.1", Version(3, 0, 0, "rc.1")),
])
def test_parse_version_valid(tag, expected):
    assert parse_version(tag) == expected


@pytest.mark.parametrize("bad", ["not-a-version", "", "1.2", "1.2.x"])
def test_parse_version_invalid(bad):
    assert parse_version(bad) is None


# --- get_latest_tag ---

def test_get_latest_tag_success():
    mock_result = MagicMock()
    mock_result.stdout = "v1.3.0\n"
    with patch("subprocess.run", return_value=mock_result):
        assert get_latest_tag() == "v1.3.0"


def test_get_latest_tag_no_tags():
    import subprocess
    with patch("subprocess.run", side_effect=subprocess.CalledProcessError(128, "git")):
        assert get_latest_tag() is None


# --- suggest_next_version ---

def test_suggest_next_patch():
    v = Version(1, 0, 0)
    assert suggest_next_version(v, ["fix", "docs"]) == Version(1, 0, 1)


def test_suggest_next_minor():
    v = Version(1, 0, 0)
    assert suggest_next_version(v, ["fix", "feat"]) == Version(1, 1, 0)


def test_suggest_next_major_breaking():
    v = Version(1, 2, 3)
    assert suggest_next_version(v, ["feat", "breaking"]) == Version(2, 0, 0)


def test_suggest_next_major_breaking_change_string():
    v = Version(2, 0, 0)
    assert suggest_next_version(v, ["BREAKING CHANGE"]) == Version(3, 0, 0)
