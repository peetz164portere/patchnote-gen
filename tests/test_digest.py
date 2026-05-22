"""Tests for patchnote_gen.digest."""

from __future__ import annotations

import pytest
from patchnote_gen.git_parser import Commit
from patchnote_gen.digest import build_digest, format_digest, DigestReport


def _commit(sha: str, type_: str, scope: str | None, msg: str, author: str = "alice") -> Commit:
    raw = f"{type_}({scope}): {msg}" if scope else f"{type_}: {msg}"
    return Commit(sha=sha, author=author, date="2024-01-01", raw_message=raw)


@pytest.fixture()
def sample_commits() -> list[Commit]:
    return [
        _commit("a1", "feat", "auth", "add OAuth2 support"),
        _commit("a2", "fix", "ui", "correct button alignment"),
        _commit("a3", "feat", "api", "expose /health endpoint"),
        _commit("a4", "chore", None, "update deps"),
        _commit("a5", "feat", "auth", "add MFA", author="bob"),
    ]


def test_build_digest_total(sample_commits):
    report = build_digest(sample_commits, since="2024-01-01", until="2024-01-07")
    assert report.total_commits == 5


def test_build_digest_by_type(sample_commits):
    report = build_digest(sample_commits, since="2024-01-01", until="2024-01-07")
    assert report.by_type["feat"] == 3
    assert report.by_type["fix"] == 1
    assert report.by_type["chore"] == 1


def test_build_digest_stores_range(sample_commits):
    report = build_digest(sample_commits, since="2024-01-01", until="2024-01-07")
    assert report.since == "2024-01-01"
    assert report.until == "2024-01-07"


def test_build_digest_highlights_non_empty(sample_commits):
    report = build_digest(sample_commits, since="2024-01-01", until="2024-01-07")
    # feat commits produce milestones
    assert len(report.highlights) > 0


def test_build_digest_top_contributors(sample_commits):
    report = build_digest(sample_commits, since="2024-01-01", until="2024-01-07")
    names = " ".join(report.top_contributors)
    assert "alice" in names
    assert "bob" in names


def test_format_digest_contains_header(sample_commits):
    report = build_digest(sample_commits, since="2024-01-01", until="2024-01-07")
    text = format_digest(report)
    assert "## Digest:" in text
    assert "2024-01-01" in text
    assert "2024-01-07" in text


def test_format_digest_breakdown_section(sample_commits):
    report = build_digest(sample_commits, since="2024-01-01", until="2024-01-07")
    text = format_digest(report)
    assert "### Breakdown by type" in text
    assert "`feat`" in text


def test_format_digest_highlights_section(sample_commits):
    report = build_digest(sample_commits, since="2024-01-01", until="2024-01-07")
    text = format_digest(report)
    assert "### Highlights" in text


def test_format_digest_contributors_section(sample_commits):
    report = build_digest(sample_commits, since="2024-01-01", until="2024-01-07")
    text = format_digest(report)
    assert "### Top contributors" in text


def test_digest_report_empty_commits():
    report = build_digest([], since="2024-01-01", until="2024-01-07")
    assert report.total_commits == 0
    assert report.by_type == {}
    assert report.highlights == []
    assert report.top_contributors == []
