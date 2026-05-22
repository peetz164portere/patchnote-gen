"""Tests for patchnote_gen.blame_cli."""
from __future__ import annotations

from unittest.mock import patch, MagicMock

import pytest

from patchnote_gen.blame_cli import build_blame_parser, main
from patchnote_gen.git_parser import Commit
from patchnote_gen.blame import BlameEntry


def _commit(sha: str, author: str) -> Commit:
    return Commit(sha=sha, author=author, raw="feat: x")


def test_build_blame_parser_defaults():
    parser = build_blame_parser()
    args = parser.parse_args([])
    assert args.since is None
    assert args.until is None
    assert args.top is None
    assert args.output is None


def test_build_blame_parser_flags():
    parser = build_blame_parser()
    args = parser.parse_args(["--since", "v1.0", "--until", "v2.0", "--top", "5"])
    assert args.since == "v1.0"
    assert args.until == "v2.0"
    assert args.top == 5


def test_main_no_commits_returns_1():
    with patch("patchnote_gen.blame_cli.get_commits", return_value=[]):
        result = main([])
    assert result == 1


def test_main_prints_to_stdout(capsys):
    commits = [_commit("abc", "Alice")]
    fake_blame = {"Alice": BlameEntry(author="Alice", files_touched=["x.py"], commit_count=1)}
    with patch("patchnote_gen.blame_cli.get_commits", return_value=commits), \
         patch("patchnote_gen.blame_cli.collect_blame", return_value=fake_blame):
        result = main([])
    assert result == 0
    captured = capsys.readouterr()
    assert "Alice" in captured.out


def test_main_writes_to_file(tmp_path):
    out_file = tmp_path / "blame.md"
    commits = [_commit("abc", "Alice")]
    fake_blame = {"Alice": BlameEntry(author="Alice", files_touched=["x.py"], commit_count=1)}
    with patch("patchnote_gen.blame_cli.get_commits", return_value=commits), \
         patch("patchnote_gen.blame_cli.collect_blame", return_value=fake_blame):
        result = main(["--output", str(out_file)])
    assert result == 0
    assert out_file.exists()
    assert "Alice" in out_file.read_text()


def test_main_top_n_passed_through(capsys):
    commits = [_commit("abc", "Alice"), _commit("def", "Bob")]
    fake_blame = {
        "Alice": BlameEntry(author="Alice", files_touched=[], commit_count=2),
        "Bob": BlameEntry(author="Bob", files_touched=[], commit_count=1),
    }
    with patch("patchnote_gen.blame_cli.get_commits", return_value=commits), \
         patch("patchnote_gen.blame_cli.collect_blame", return_value=fake_blame):
        result = main(["--top", "1"])
    assert result == 0
    captured = capsys.readouterr()
    assert "Alice" in captured.out
    assert "Bob" not in captured.out
