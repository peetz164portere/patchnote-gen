"""Tests for patchnote_gen.search."""

import pytest

from patchnote_gen.git_parser import Commit
from patchnote_gen.search import (
    SearchQuery,
    SearchResult,
    format_search_results,
    search_commits,
)


def _commit(
    sha="abc1234",
    message="feat: add thing",
    author="Alice <alice@example.com>",
    body="",
    commit_type="feat",
    scope=None,
):
    c = Commit(sha=sha, message=message, author=author, body=body)
    c._type = commit_type
    c._scope = scope
    return c


@pytest.fixture
def sample_commits():
    return [
        _commit(sha="aaa", message="feat(auth): add login", commit_type="feat", scope="auth", author="Alice"),
        _commit(sha="bbb", message="fix: resolve crash", commit_type="fix", scope=None, author="Bob"),
        _commit(sha="ccc", message="chore: update deps", commit_type="chore", scope=None, author="Alice"),
        _commit(sha="ddd", message="feat(api): expose endpoint", commit_type="feat", scope="api", author="Carol"),
    ]


def test_search_by_type(sample_commits):
    results = search_commits(sample_commits, SearchQuery(types=["feat"]))
    assert len(results) == 2
    assert all(r.commit.commit_type == "feat" for r in results)


def test_search_by_scope(sample_commits):
    results = search_commits(sample_commits, SearchQuery(scopes=["auth"]))
    assert len(results) == 1
    assert results[0].commit.sha == "aaa"


def test_search_by_author(sample_commits):
    results = search_commits(sample_commits, SearchQuery(authors=["Alice"]))
    assert len(results) == 2


def test_search_by_text_substring(sample_commits):
    results = search_commits(sample_commits, SearchQuery(text="crash"))
    assert len(results) == 1
    assert results[0].commit.sha == "bbb"


def test_search_text_case_insensitive(sample_commits):
    results = search_commits(sample_commits, SearchQuery(text="CRASH", case_sensitive=False))
    assert len(results) == 1


def test_search_text_case_sensitive_no_match(sample_commits):
    results = search_commits(sample_commits, SearchQuery(text="CRASH", case_sensitive=True))
    assert len(results) == 0


def test_search_text_regex(sample_commits):
    results = search_commits(sample_commits, SearchQuery(text=r"feat\(\w+\)", regex=True))
    assert len(results) == 2


def test_search_combined_type_and_scope(sample_commits):
    results = search_commits(sample_commits, SearchQuery(types=["feat"], scopes=["api"]))
    assert len(results) == 1
    assert results[0].commit.sha == "ddd"


def test_search_no_criteria_returns_all(sample_commits):
    results = search_commits(sample_commits, SearchQuery())
    assert len(results) == len(sample_commits)


def test_search_result_str():
    c = _commit(sha="abc1234abcd", message="fix: something")
    r = SearchResult(commit=c, matched_fields=["message"])
    text = str(r)
    assert "abc1234" in text
    assert "message" in text


def test_format_search_results_empty():
    out = format_search_results([])
    assert "No commits" in out


def test_format_search_results_non_empty(sample_commits):
    results = search_commits(sample_commits, SearchQuery(types=["fix"]))
    out = format_search_results(results)
    assert "Found 1 commit" in out
    assert "resolve crash" in out
