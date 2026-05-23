"""Tests for patchnote_gen.revert."""

from __future__ import annotations

import pytest

from patchnote_gen.git_parser import Commit
from patchnote_gen.revert import (
    RevertEntry,
    RevertReport,
    _extract_target_sha,
    collect_reverts,
    build_revert_report,
    format_revert_report,
)


def _commit(
    hash: str = "abc1234",
    commit_type: str = "feat",
    scope: str = "",
    message: str = "do something",
    author: str = "dev",
) -> Commit:
    return Commit(
        hash=hash,
        commit_type=commit_type,
        scope=scope,
        message=message,
        author=author,
        date="2024-01-01",
    )


# ---------------------------------------------------------------------------
# _extract_target_sha
# ---------------------------------------------------------------------------

def test_extract_sha_from_standard_message():
    msg = "Revert \"feat: add login\"\n\nThis reverts commit abc1234def5678."
    assert _extract_target_sha(msg) == "abc1234def5678"


def test_extract_sha_short_form():
    msg = "reverts abc1234"
    assert _extract_target_sha(msg) == "abc1234"


def test_extract_sha_returns_none_when_absent():
    assert _extract_target_sha("just a plain message") is None


# ---------------------------------------------------------------------------
# collect_reverts
# ---------------------------------------------------------------------------

def test_collect_reverts_picks_revert_type():
    commits = [
        _commit(hash="aaa0001", commit_type="feat", message="add feature"),
        _commit(hash="bbb0002", commit_type="revert", message="This reverts commit aaa0001."),
        _commit(hash="ccc0003", commit_type="fix", message="fix bug"),
    ]
    result = collect_reverts(commits)
    assert len(result) == 1
    assert result[0].reverting.hash == "bbb0002"
    assert result[0].target_sha == "aaa0001"


def test_collect_reverts_empty_when_none():
    commits = [_commit(commit_type="feat"), _commit(commit_type="fix")]
    assert collect_reverts(commits) == []


def test_collect_reverts_target_sha_none_when_unparseable():
    c = _commit(hash="fff0001", commit_type="revert", message="revert something vague")
    result = collect_reverts([c])
    assert result[0].target_sha is None


# ---------------------------------------------------------------------------
# build_revert_report
# ---------------------------------------------------------------------------

def test_build_revert_report_total():
    commits = [
        _commit(commit_type="revert", message="This reverts commit abc1234."),
        _commit(commit_type="revert", message="This reverts commit def5678."),
        _commit(commit_type="feat"),
    ]
    report = build_revert_report(commits, since="v1.0", until="v2.0")
    assert report.total == 2
    assert report.since == "v1.0"
    assert report.until == "v2.0"


# ---------------------------------------------------------------------------
# format / __str__
# ---------------------------------------------------------------------------

def test_format_revert_report_no_reverts():
    report = RevertReport()
    assert format_revert_report(report) == "No reverts found."


def test_format_revert_report_lists_entries():
    c = _commit(hash="abc1234", commit_type="revert", message="undo login feature")
    entry = RevertEntry(reverting=c, target_sha="def5678")
    report = RevertReport(reverts=[entry])
    text = format_revert_report(report)
    assert "abc1234" in text
    assert "def5678" in text


def test_revert_entry_str_unknown_sha():
    c = _commit(hash="abc1234", commit_type="revert", message="vague revert")
    entry = RevertEntry(reverting=c, target_sha=None)
    assert "unknown" in str(entry)
