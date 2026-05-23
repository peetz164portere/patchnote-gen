"""Tests for patchnote_gen.timeline_cli."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from patchnote_gen.timeline_cli import build_timeline_parser, main

_JAN_05 = int(datetime(2024, 1, 5, tzinfo=timezone.utc).timestamp())
_FEB_10 = int(datetime(2024, 2, 10, tzinfo=timezone.utc).timestamp())


def _make_commit(ts: int, msg: str = "feat: x") -> MagicMock:
    c = MagicMock()
    c.date = str(ts)
    c.message = msg
    c.author = "alice"
    c.hash = "aabbccdd1234"
    return c


def test_build_timeline_parser_defaults():
    parser = build_timeline_parser()
    args = parser.parse_args([])
    assert args.period == "month"
    assert args.since is None
    assert args.until is None
    assert args.markdown is False


def test_build_timeline_parser_flags():
    parser = build_timeline_parser()
    args = parser.parse_args(["--period", "week", "--since", "v1.0", "--markdown"])
    assert args.period == "week"
    assert args.since == "v1.0"
    assert args.markdown is True


def test_main_no_commits_returns_1():
    with patch("patchnote_gen.timeline_cli.get_commits", return_value=[]):
        result = main([])
    assert result == 1


def test_main_prints_summary(capsys):
    commits = [_make_commit(_JAN_05), _make_commit(_FEB_10)]
    with patch("patchnote_gen.timeline_cli.get_commits", return_value=commits):
        result = main(["--period", "month"])
    assert result == 0
    out = capsys.readouterr().out
    assert "Timeline" in out


def test_main_prints_markdown(capsys):
    commits = [_make_commit(_JAN_05, "feat: nice")]
    with patch("patchnote_gen.timeline_cli.get_commits", return_value=commits):
        result = main(["--markdown"])
    assert result == 0
    out = capsys.readouterr().out
    assert "## Commit Timeline" in out


def test_main_passes_since_until():
    commits = [_make_commit(_JAN_05)]
    with patch("patchnote_gen.timeline_cli.get_commits", return_value=commits) as mock_gc:
        main(["--since", "v1.0", "--until", "v2.0"])
    mock_gc.assert_called_once_with(since="v1.0", until="v2.0")
