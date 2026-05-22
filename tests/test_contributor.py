"""Tests for patchnote_gen.contributor."""
import pytest
from patchnote_gen.contributor import (
    ContributorStat,
    collect_contributors,
    format_contributors,
)
from patchnote_gen.git_parser import Commit


def _commit(author: str, email: str, ctype: str | None = "feat") -> Commit:
    raw = f"{ctype}(scope): message" if ctype else "plain message"
    c = Commit(hash="abc1234", raw_message=raw, author=author, author_email=email)
    return c


@pytest.fixture
def sample_commits():
    return [
        _commit("Alice", "alice@example.com", "feat"),
        _commit("Alice", "alice@example.com", "fix"),
        _commit("Bob", "bob@example.com", "feat"),
        _commit("Alice", "alice@example.com", "feat"),
        _commit("Carol", "carol@example.com", None),
    ]


def test_collect_contributors_count(sample_commits):
    stats = collect_contributors(sample_commits)
    names = [s.name for s in stats]
    assert "Alice" in names
    assert "Bob" in names


def test_collect_contributors_sorted_by_count(sample_commits):
    stats = collect_contributors(sample_commits)
    assert stats[0].name == "Alice"
    assert stats[0].commit_count == 3


def test_collect_contributors_type_tally(sample_commits):
    stats = collect_contributors(sample_commits)
    alice = next(s for s in stats if s.name == "Alice")
    assert alice.types["feat"] == 2
    assert alice.types["fix"] == 1


def test_collect_contributors_top_type(sample_commits):
    stats = collect_contributors(sample_commits)
    alice = next(s for s in stats if s.name == "Alice")
    assert alice.top_type == "feat"


def test_collect_contributors_no_author():
    c = Commit(hash="000", raw_message="feat: something", author=None, author_email="")
    stats = collect_contributors([c])
    assert stats == []


def test_collect_contributors_empty():
    assert collect_contributors([]) == []


def test_contributor_stat_str():
    s = ContributorStat(name="Alice", email="a@b.com", commit_count=5)
    assert "Alice" in str(s)
    assert "5 commits" in str(s)


def test_format_contributors_markdown(sample_commits):
    stats = collect_contributors(sample_commits)
    output = format_contributors(stats, markdown=True)
    assert "| Author |" in output
    assert "Alice" in output
    assert "feat" in output


def test_format_contributors_plain(sample_commits):
    stats = collect_contributors(sample_commits)
    output = format_contributors(stats, markdown=False)
    assert "Contributors:" in output
    assert "Alice" in output
    assert "|" not in output


def test_format_contributors_empty():
    result = format_contributors([])
    assert "No contributors" in result
