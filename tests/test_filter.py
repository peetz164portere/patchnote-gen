"""Tests for patchnote_gen.filter module."""

import pytest
from patchnote_gen.git_parser import Commit
from patchnote_gen.filter import filter_commits, _is_breaking


@pytest.fixture
def sample_commits():
    return [
        Commit(hash="a1", subject="feat(auth): add login", body=""),
        Commit(hash="a2", subject="fix(auth): fix token expiry", body=""),
        Commit(hash="a3", subject="chore: update deps", body=""),
        Commit(hash="a4", subject="feat(ui): add dark mode", body=""),
        Commit(hash="a5", subject="fix: patch null pointer", body=""),
        Commit(hash="a6", subject="feat!: drop python 3.7", body="BREAKING CHANGE: requires 3.9+"),
    ]


def test_filter_by_include_types(sample_commits):
    result = filter_commits(sample_commits, include_types=["feat"])
    assert all(c.commit_type == "feat" for c in result)
    assert len(result) == 3


def test_filter_by_exclude_types(sample_commits):
    result = filter_commits(sample_commits, exclude_types=["chore"])
    assert all(c.commit_type != "chore" for c in result)
    assert len(result) == 5


def test_filter_by_scope(sample_commits):
    result = filter_commits(sample_commits, scope="auth")
    assert len(result) == 2
    assert all(c.scope == "auth" for c in result)


def test_filter_scope_case_insensitive(sample_commits):
    result = filter_commits(sample_commits, scope="AUTH")
    assert len(result) == 2


def test_filter_breaking_only(sample_commits):
    result = filter_commits(sample_commits, breaking_only=True)
    assert len(result) == 1
    assert result[0].hash == "a6"


def test_filter_no_criteria_returns_all(sample_commits):
    result = filter_commits(sample_commits)
    assert result == sample_commits


def test_filter_combined(sample_commits):
    result = filter_commits(sample_commits, include_types=["feat"], scope="auth")
    assert len(result) == 1
    assert result[0].hash == "a1"


def test_filter_empty_list():
    assert filter_commits([]) == []


def test_is_breaking_with_footer():
    c = Commit(hash="x", subject="feat: something", body="BREAKING CHANGE: removed API")
    assert _is_breaking(c) is True


def test_is_breaking_false_for_normal():
    c = Commit(hash="y", subject="fix: minor", body="")
    assert _is_breaking(c) is False
