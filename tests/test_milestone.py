"""Tests for patchnote_gen.milestone."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from patchnote_gen.git_parser import Commit
from patchnote_gen.milestone import (
    Milestone,
    detect_milestones,
    format_milestones,
)
from patchnote_gen.milestone_cli import build_milestone_parser, main


def _commit(ctype: str, msg: str, scope: str = "", raw_body: str = "") -> Commit:
    c = Commit(hash="abc1234", raw="raw", author="dev", date="2024-01-01")
    c.commit_type = ctype
    c.scope = scope
    c.message = msg
    c.raw_body = raw_body
    return c


# --- detect_milestones ---

def test_detect_milestones_feat_is_highlight():
    commits = [_commit("feat", "add dark mode")]
    result = detect_milestones(commits)
    assert len(result) == 1
    assert result[0].reason == "feat"
    assert result[0].priority == 1


def test_detect_milestones_fix_is_highlight():
    commits = [_commit("fix", "patch null pointer")]
    result = detect_milestones(commits)
    assert len(result) == 1
    assert result[0].reason == "fix"


def test_detect_milestones_breaking_highest_priority():
    commits = [
        _commit("feat", "new api"),
        _commit("fix", "remove endpoint", raw_body="BREAKING CHANGE: removed /v1/users"),
    ]
    result = detect_milestones(commits)
    assert result[0].reason == "breaking"
    assert result[0].priority == 0


def test_detect_milestones_chore_skipped():
    commits = [_commit("chore", "update deps")]
    result = detect_milestones(commits)
    assert result == []


def test_detect_milestones_extra_types():
    commits = [_commit("docs", "improve readme")]
    result = detect_milestones(commits, extra_highlight_types=["docs"])
    assert len(result) == 1
    assert result[0].reason == "docs"


def test_milestone_str_with_scope():
    c = _commit("feat", "add oauth", scope="auth")
    ms = Milestone(commit=c, reason="feat", priority=1)
    assert "(auth)" in str(ms)
    assert "add oauth" in str(ms)


# --- format_milestones ---

def test_format_milestones_empty_returns_empty():
    assert format_milestones([]) == ""


def test_format_milestones_contains_title():
    commits = [_commit("feat", "new thing")]
    milestones = detect_milestones(commits)
    output = format_milestones(milestones, title="Highlights")
    assert "## Highlights" in output


def test_format_milestones_badge_uppercase():
    commits = [_commit("feat", "cool feature")]
    milestones = detect_milestones(commits)
    output = format_milestones(milestones)
    assert "`FEAT`" in output


# --- CLI ---

def test_build_milestone_parser_defaults():
    parser = build_milestone_parser()
    args = parser.parse_args([])
    assert args.until == "HEAD"
    assert args.since is None
    assert args.plain is False
    assert args.title == "Release Highlights"


def test_main_no_commits_returns_1():
    with patch("patchnote_gen.milestone_cli.get_commits", return_value=[]):
        assert main([]) == 1


def test_main_no_milestones_returns_0():
    commits = [_commit("chore", "cleanup")]
    with patch("patchnote_gen.milestone_cli.get_commits", return_value=commits):
        assert main([]) == 0


def test_main_plain_output(capsys):
    commits = [_commit("feat", "shiny feature")]
    with patch("patchnote_gen.milestone_cli.get_commits", return_value=commits):
        rc = main(["--plain"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "shiny feature" in captured.out
