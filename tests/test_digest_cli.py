"""Tests for patchnote_gen.digest_cli."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from patchnote_gen.git_parser import Commit
from patchnote_gen.digest_cli import build_digest_parser, main


def _commit(sha: str, type_: str, msg: str, author: str = "alice") -> Commit:
    return Commit(sha=sha, author=author, date="2024-01-01", raw_message=f"{type_}: {msg}")


_SAMPLE = [
    _commit("c1", "feat", "new widget"),
    _commit("c2", "fix", "null pointer"),
]


def test_build_digest_parser_defaults():
    parser = build_digest_parser()
    args = parser.parse_args([])
    assert args.since == "1 week ago"
    assert args.repo == "."
    assert args.output is None


def test_build_digest_parser_flags():
    parser = build_digest_parser()
    args = parser.parse_args(["--since", "2024-01-01", "--until", "2024-01-07", "--repo", "/tmp"])
    assert args.since == "2024-01-01"
    assert args.until == "2024-01-07"
    assert args.repo == "/tmp"


def test_main_no_commits_returns_1():
    with patch("patchnote_gen.digest_cli.get_commits", return_value=[]):
        result = main(["--since", "2024-01-01"])
    assert result == 1


def test_main_prints_to_stdout(capsys):
    with patch("patchnote_gen.digest_cli.get_commits", return_value=_SAMPLE):
        result = main(["--since", "2024-01-01", "--until", "2024-01-07"])
    assert result == 0
    captured = capsys.readouterr()
    assert "Digest:" in captured.out


def test_main_writes_to_file(tmp_path):
    out_file = tmp_path / "digest.md"
    with patch("patchnote_gen.digest_cli.get_commits", return_value=_SAMPLE):
        result = main(["--since", "2024-01-01", "--output", str(out_file)])
    assert result == 0
    assert out_file.exists()
    content = out_file.read_text(encoding="utf-8")
    assert "Digest:" in content


def test_main_file_contains_type_breakdown(tmp_path):
    out_file = tmp_path / "digest.md"
    with patch("patchnote_gen.digest_cli.get_commits", return_value=_SAMPLE):
        main(["--since", "2024-01-01", "--output", str(out_file)])
    content = out_file.read_text(encoding="utf-8")
    assert "`feat`" in content or "`fix`" in content
