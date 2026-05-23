"""Tests for patchnote_gen.scope_map."""

from __future__ import annotations

import pytest

from patchnote_gen.git_parser import Commit
from patchnote_gen.scope_map import (
    ScopeEntry,
    build_scope_map,
    format_scope_map,
    top_scopes,
)


def _commit(sha, ctype, scope, author="alice"):
    return Commit(
        sha=sha,
        message=f"{ctype}({scope}): msg" if scope else f"{ctype}: msg",
        author=author,
        date="2024-01-01",
    )


@pytest.fixture
def sample_commits():
    return [
        _commit("a1", "feat", "auth"),
        _commit("a2", "fix", "auth"),
        _commit("a3", "feat", "auth", author="bob"),
        _commit("b1", "chore", "ci"),
        _commit("c1", "docs", ""),
        _commit("c2", "docs", ""),
    ]


def test_build_scope_map_groups_by_scope(sample_commits):
    result = build_scope_map(sample_commits)
    assert "auth" in result
    assert result["auth"].count == 3


def test_build_scope_map_no_scope_filed_under_none(sample_commits):
    result = build_scope_map(sample_commits)
    assert "(none)" in result
    assert result["(none)"].count == 2


def test_build_scope_map_scope_normalised_to_lowercase():
    commits = [
        _commit("x1", "feat", "Auth"),
        _commit("x2", "fix", "auth"),
    ]
    result = build_scope_map(commits)
    assert "auth" in result
    assert result["auth"].count == 2


def test_scope_entry_types(sample_commits):
    result = build_scope_map(sample_commits)
    types = result["auth"].types
    assert "feat" in types
    assert "fix" in types


def test_scope_entry_authors(sample_commits):
    result = build_scope_map(sample_commits)
    authors = result["auth"].authors
    assert "alice" in authors
    assert "bob" in authors


def test_scope_entry_str():
    entry = ScopeEntry(scope="auth")
    entry.commits = [_commit("z1", "feat", "auth")]
    text = str(entry)
    assert "auth" in text
    assert "1 commit" in text


def test_top_scopes_returns_n(sample_commits):
    mapping = build_scope_map(sample_commits)
    top = top_scopes(mapping, n=1)
    assert len(top) == 1
    assert top[0].scope == "auth"


def test_top_scopes_sorted_descending(sample_commits):
    mapping = build_scope_map(sample_commits)
    top = top_scopes(mapping)
    counts = [e.count for e in top]
    assert counts == sorted(counts, reverse=True)


def test_format_scope_map_contains_scope_names(sample_commits):
    mapping = build_scope_map(sample_commits)
    output = format_scope_map(mapping)
    assert "auth" in output
    assert "ci" in output


def test_format_scope_map_empty():
    output = format_scope_map({})
    assert "No scoped commits" in output


def test_format_scope_map_limit(sample_commits):
    mapping = build_scope_map(sample_commits)
    output = format_scope_map(mapping, limit=1)
    # Only the top scope (auth) should appear
    assert "auth" in output
    assert "ci" not in output
