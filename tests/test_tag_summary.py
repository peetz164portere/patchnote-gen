"""Tests for patchnote_gen.tag_summary and tag_summary_cli."""
from __future__ import annotations

from unittest.mock import patch

import pytest

from patchnote_gen.git_parser import Commit
from patchnote_gen.tag_summary import build_tag_summary, format_tag_summary, TagSummary
from patchnote_gen.tag_summary_cli import build_tag_summary_parser, main


def _commit(sha, msg, author="alice"):
    return Commit(sha=sha, message=msg, author=author, date="2024-01-01")


SAMPLE = [
    _commit("aaa", "feat(auth): add login"),
    _commit("bbb", "fix(auth): null check"),
    _commit("ccc", "chore: update deps"),
]


# ---------------------------------------------------------------------------
# build_tag_summary
# ---------------------------------------------------------------------------

def test_build_tag_summary_passes_ref_range():
    with patch("patchnote_gen.tag_summary.get_commits", return_value=SAMPLE) as mock_gc:
        result = build_tag_summary("v1.0.0", "v2.0.0")
    mock_gc.assert_called_once_with(since=None, until=None, ref_range="v1.0.0..v2.0.0")
    assert result.from_tag == "v1.0.0"
    assert result.to_tag == "v2.0.0"
    assert len(result.commits) == 3


def test_build_tag_summary_default_to_head():
    with patch("patchnote_gen.tag_summary.get_commits", return_value=SAMPLE):
        result = build_tag_summary("v1.0.0")
    assert result.to_tag == "HEAD"


def test_build_tag_summary_stats_populated():
    with patch("patchnote_gen.tag_summary.get_commits", return_value=SAMPLE):
        result = build_tag_summary("v1.0.0")
    assert result.stats is not None
    assert result.stats.total == 3


def test_build_tag_summary_no_commits_stats_none():
    with patch("patchnote_gen.tag_summary.get_commits", return_value=[]):
        result = build_tag_summary("v1.0.0")
    assert result.stats is None
    assert result.commits == []


# ---------------------------------------------------------------------------
# format_tag_summary
# ---------------------------------------------------------------------------

def test_format_tag_summary_header():
    with patch("patchnote_gen.tag_summary.get_commits", return_value=SAMPLE):
        summary = build_tag_summary("v1.0.0", "v2.0.0")
    text = format_tag_summary(summary)
    assert "v1.0.0" in text
    assert "v2.0.0" in text


def test_format_tag_summary_total_count():
    with patch("patchnote_gen.tag_summary.get_commits", return_value=SAMPLE):
        summary = build_tag_summary("v1.0.0")
    text = format_tag_summary(summary)
    assert "3" in text


def test_format_tag_summary_by_type_listed():
    with patch("patchnote_gen.tag_summary.get_commits", return_value=SAMPLE):
        summary = build_tag_summary("v1.0.0")
    text = format_tag_summary(summary)
    assert "feat" in text
    assert "fix" in text


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def test_build_tag_summary_parser_defaults():
    parser = build_tag_summary_parser()
    args = parser.parse_args(["v1.0.0"])
    assert args.from_tag == "v1.0.0"
    assert args.to_tag == "HEAD"
    assert args.plain is False


def test_build_tag_summary_parser_all_flags():
    parser = build_tag_summary_parser()
    args = parser.parse_args(["v1.0.0", "v2.0.0", "--plain"])
    assert args.to_tag == "v2.0.0"
    assert args.plain is True


def test_main_no_commits_returns_1():
    with patch("patchnote_gen.tag_summary.get_commits", return_value=[]):
        rc = main(["v1.0.0", "v2.0.0"])
    assert rc == 1


def test_main_prints_summary(capsys):
    with patch("patchnote_gen.tag_summary.get_commits", return_value=SAMPLE):
        rc = main(["v1.0.0", "v2.0.0"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "v1.0.0" in out


def test_main_plain_strips_header(capsys):
    with patch("patchnote_gen.tag_summary.get_commits", return_value=SAMPLE):
        rc = main(["v1.0.0", "v2.0.0", "--plain"])
    assert rc == 0
    out = capsys.readouterr().out
    assert not out.startswith("##")
