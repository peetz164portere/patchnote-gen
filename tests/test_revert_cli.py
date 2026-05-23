"""Tests for patchnote_gen.revert_cli."""

from __future__ import annotations

from unittest.mock import patch, MagicMock

import pytest

from patchnote_gen.revert_cli import build_revert_parser, main
from patchnote_gen.git_parser import Commit
from patchnote_gen.revert import RevertReport, RevertEntry


def _commit(
    hash: str = "abc1234",
    commit_type: str = "revert",
    message: str = "This reverts commit def5678.",
) -> Commit:
    return Commit(
        hash=hash,
        commit_type=commit_type,
        scope="",
        message=message,
        author="dev",
        date="2024-01-01",
    )


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

def test_build_revert_parser_defaults():
    p = build_revert_parser()
    args = p.parse_args([])
    assert args.since == ""
    assert args.until == "HEAD"
    assert args.repo == "."
    assert args.json is False


def test_build_revert_parser_flags():
    p = build_revert_parser()
    args = p.parse_args(["--since", "v1.0", "--until", "v2.0", "--json"])
    assert args.since == "v1.0"
    assert args.until == "v2.0"
    assert args.json is True


# ---------------------------------------------------------------------------
# main()
# ---------------------------------------------------------------------------

def test_main_no_commits_returns_1(capsys):
    with patch("patchnote_gen.revert_cli.get_commits", return_value=[]):
        rc = main([])
    assert rc == 1
    captured = capsys.readouterr()
    assert "No commits" in captured.err


def test_main_prints_plain_text(capsys):
    commits = [_commit()]
    with patch("patchnote_gen.revert_cli.get_commits", return_value=commits):
        rc = main([])
    assert rc == 0
    out = capsys.readouterr().out
    assert "revert" in out.lower() or "Revert" in out


def test_main_prints_json(capsys):
    commits = [_commit(hash="abc1234", message="This reverts commit def5678.")]
    with patch("patchnote_gen.revert_cli.get_commits", return_value=commits):
        rc = main(["--json"])
    assert rc == 0
    import json
    data = json.loads(capsys.readouterr().out)
    assert isinstance(data, list)
    assert data[0]["hash"] == "abc1234"


def test_main_no_reverts_shows_none_found(capsys):
    commits = [
        Commit(hash="aaa", commit_type="feat", scope="", message="add thing", author="dev", date="2024-01-01"),
    ]
    with patch("patchnote_gen.revert_cli.get_commits", return_value=commits):
        rc = main([])
    assert rc == 0
    assert "No reverts" in capsys.readouterr().out
