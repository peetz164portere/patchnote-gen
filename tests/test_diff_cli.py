"""Tests for patchnote_gen.diff_cli."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from patchnote_gen.diff_cli import build_diff_parser, main
from patchnote_gen.diff_stats import DiffStat
from patchnote_gen.git_parser import Commit


def _make_commit(sha: str) -> Commit:
    c = Commit(sha=sha, raw="feat: something")
    return c


def test_build_diff_parser_defaults():
    parser = build_diff_parser()
    args = parser.parse_args([])
    assert args.since is None
    assert args.until == "HEAD"
    assert args.summary is False
    assert args.repo == "."


def test_build_diff_parser_flags():
    parser = build_diff_parser()
    args = parser.parse_args(["--since", "v1.0", "--until", "v2.0", "--summary", "--repo", "/tmp"])
    assert args.since == "v1.0"
    assert args.until == "v2.0"
    assert args.summary is True
    assert args.repo == "/tmp"


@patch("patchnote_gen.diff_cli.get_commits", return_value=[])
def test_main_no_commits_returns_1(mock_gc):
    rc = main([])
    assert rc == 1


@patch("patchnote_gen.diff_cli.get_diff_stats", return_value=[])
@patch(
    "patchnote_gen.diff_cli.get_commits",
    return_value=[_make_commit("abc1234")],
)
def test_main_no_stats_returns_1(mock_gc, mock_gs):
    rc = main([])
    assert rc == 1


@patch(
    "patchnote_gen.diff_cli.get_diff_stats",
    return_value=[
        DiffStat(sha="abc1234", files_changed=1, insertions=5, deletions=2),
    ],
)
@patch(
    "patchnote_gen.diff_cli.get_commits",
    return_value=[_make_commit("abc1234")],
)
def test_main_prints_per_commit(mock_gc, mock_gs, capsys):
    rc = main([])
    assert rc == 0
    out = capsys.readouterr().out
    assert "abc1234" in out
    assert "+5" in out


@patch(
    "patchnote_gen.diff_cli.get_diff_stats",
    return_value=[
        DiffStat(sha="abc1234", files_changed=2, insertions=10, deletions=3),
    ],
)
@patch(
    "patchnote_gen.diff_cli.get_commits",
    return_value=[_make_commit("abc1234")],
)
def test_main_summary_flag(mock_gc, mock_gs, capsys):
    rc = main(["--summary"])
    assert rc == 0
    out = capsys.readouterr().out
    # per-commit lines should NOT appear
    assert "abc1234" not in out
    assert "Total:" in out
    assert "+10" in out


@patch(
    "patchnote_gen.diff_cli.get_diff_stats",
    return_value=[
        DiffStat(sha="aaa", files_changed=1, insertions=4, deletions=4),
        DiffStat(sha="bbb", files_changed=2, insertions=6, deletions=1),
    ],
)
@patch(
    "patchnote_gen.diff_cli.get_commits",
    return_value=[_make_commit("aaa"), _make_commit("bbb")],
)
def test_main_net_lines_in_summary(mock_gc, mock_gs, capsys):
    rc = main(["--summary"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "net +5" in out
