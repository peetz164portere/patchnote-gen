"""Tests for patchnote_gen.blame."""
from __future__ import annotations

from unittest.mock import patch

import pytest

from patchnote_gen.blame import BlameEntry, collect_blame, format_blame
from patchnote_gen.git_parser import Commit


def _commit(sha: str, author: str, msg: str = "feat: something") -> Commit:
    return Commit(sha=sha, author=author, raw=msg)


@pytest.fixture()
def sample_commits():
    return [
        _commit("aaa", "Alice", "feat: add login"),
        _commit("bbb", "Bob", "fix: typo"),
        _commit("ccc", "Alice", "chore: cleanup"),
    ]


def _fake_files(sha: str):
    mapping = {
        "aaa": ["auth.py", "tests/test_auth.py"],
        "bbb": ["README.md"],
        "ccc": ["auth.py"],
    }
    return mapping.get(sha, [])


def test_collect_blame_counts_commits(sample_commits):
    with patch("patchnote_gen.blame._files_for_commit", side_effect=_fake_files):
        blame = collect_blame(sample_commits)
    assert blame["Alice"].commit_count == 2
    assert blame["Bob"].commit_count == 1


def test_collect_blame_deduplicates_files(sample_commits):
    with patch("patchnote_gen.blame._files_for_commit", side_effect=_fake_files):
        blame = collect_blame(sample_commits)
    # auth.py appears in both Alice's commits but should only be listed once
    assert blame["Alice"].files_touched.count("auth.py") == 1


def test_collect_blame_all_authors(sample_commits):
    with patch("patchnote_gen.blame._files_for_commit", return_value=[]):
        blame = collect_blame(sample_commits)
    assert set(blame.keys()) == {"Alice", "Bob"}


def test_format_blame_returns_table(sample_commits):
    with patch("patchnote_gen.blame._files_for_commit", side_effect=_fake_files):
        blame = collect_blame(sample_commits)
    output = format_blame(blame)
    assert "| Author |" in output
    assert "Alice" in output
    assert "Bob" in output


def test_format_blame_top_n(sample_commits):
    with patch("patchnote_gen.blame._files_for_commit", side_effect=_fake_files):
        blame = collect_blame(sample_commits)
    output = format_blame(blame, top_n=1)
    assert "Alice" in output
    assert "Bob" not in output


def test_format_blame_empty():
    output = format_blame({})
    assert "No blame data" in output


def test_blame_entry_str():
    entry = BlameEntry(author="Carol", files_touched=["a.py", "b.py"], commit_count=3)
    text = str(entry)
    assert "Carol" in text
    assert "3" in text
