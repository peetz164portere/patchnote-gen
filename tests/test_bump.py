"""Tests for patchnote_gen.bump."""

from unittest.mock import patch, MagicMock
from patchnote_gen.bump import (
    collect_commit_types,
    resolve_current_version,
    compute_next_version,
)
from patchnote_gen.version_tagger import Version


_FAKE_COMMITS = [
    MagicMock(subject="feat(auth): add login"),
    MagicMock(subject="fix(ui): correct button color"),
    MagicMock(subject="chore: update deps"),
    MagicMock(subject="not conventional at all"),
]


def test_collect_commit_types_returns_types():
    with patch("patchnote_gen.bump.get_commits", return_value=_FAKE_COMMITS):
        types = collect_commit_types(since="v1.0.0")
    assert "feat" in types
    assert "fix" in types
    assert "chore" in types


def test_collect_commit_types_deduplicates():
    dupes = [
        MagicMock(subject="feat: a"),
        MagicMock(subject="feat: b"),
        MagicMock(subject="fix: c"),
    ]
    with patch("patchnote_gen.bump.get_commits", return_value=dupes):
        types = collect_commit_types(since=None)
    assert types.count("feat") == 1


def test_collect_commit_types_skips_non_conventional():
    commits = [MagicMock(subject="not conventional")]
    with patch("patchnote_gen.bump.get_commits", return_value=commits):
        types = collect_commit_types(since=None)
    assert types == []


def test_resolve_current_version_from_override():
    v = resolve_current_version(override="2.5.1")
    assert v == Version(2, 5, 1)


def test_resolve_current_version_from_tag():
    with patch("patchnote_gen.bump.get_latest_tag", return_value="v1.0.0"):
        v = resolve_current_version()
    assert v == Version(1, 0, 0)


def test_resolve_current_version_no_tag():
    with patch("patchnote_gen.bump.get_latest_tag", return_value=None):
        v = resolve_current_version()
    assert v is None


def test_compute_next_version_feat_bumps_minor():
    with patch("patchnote_gen.bump.collect_commit_types", return_value=["feat", "fix"]), \
         patch("patchnote_gen.bump.resolve_current_version", return_value=Version(1, 2, 3)):
        result = compute_next_version()
    assert result == (Version(1, 2, 3), Version(1, 3, 0))


def test_compute_next_version_fix_only_bumps_patch():
    with patch("patchnote_gen.bump.collect_commit_types", return_value=["fix"]), \
         patch("patchnote_gen.bump.resolve_current_version", return_value=Version(0, 9, 4)):
        result = compute_next_version()
    assert result == (Version(0, 9, 4), Version(0, 9, 5))


def test_compute_next_version_no_current_returns_none():
    with patch("patchnote_gen.bump.resolve_current_version", return_value=None):
        result = compute_next_version()
    assert result is None
