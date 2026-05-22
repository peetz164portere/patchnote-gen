"""Tests for patchnote_gen.diff_stats."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from patchnote_gen.diff_stats import (
    DiffStat,
    get_diff_stat,
    get_diff_stats,
    summarise_stats,
)

STAT_OUTPUT = """
 patchnote_gen/foo.py | 15 +++++++++------
 patchnote_gen/bar.py |  4 ++--
 2 files changed, 11 insertions(+), 6 deletions(-)
"""


def _mock_run(output: str):
    result = MagicMock()
    result.stdout = output
    return result


def test_diff_stat_str():
    s = DiffStat(sha="abc", files_changed=2, insertions=11, deletions=6)
    assert str(s) == "2 file(s) changed, +11 -6"


def test_diff_stat_net_lines():
    s = DiffStat(sha="abc", insertions=10, deletions=3)
    assert s.net_lines == 7


@patch("patchnote_gen.diff_stats.subprocess.run")
def test_get_diff_stat_parses_output(mock_run):
    mock_run.return_value = _mock_run(STAT_OUTPUT)
    stat = get_diff_stat("abc123")
    assert stat is not None
    assert stat.sha == "abc123"
    assert stat.files_changed == 2
    assert stat.insertions == 11
    assert stat.deletions == 6
    assert "patchnote_gen/foo.py" in stat.files
    assert "patchnote_gen/bar.py" in stat.files


@patch("patchnote_gen.diff_stats.subprocess.run")
def test_get_diff_stat_returns_none_on_error(mock_run):
    import subprocess
    mock_run.side_effect = subprocess.CalledProcessError(1, "git")
    stat = get_diff_stat("deadbeef")
    assert stat is None


@patch("patchnote_gen.diff_stats.subprocess.run")
def test_get_diff_stat_no_deletions(mock_run):
    output = " src/x.py | 5 +++++\n 1 file changed, 5 insertions(+)\n"
    mock_run.return_value = _mock_run(output)
    stat = get_diff_stat("aaa")
    assert stat.insertions == 5
    assert stat.deletions == 0


@patch("patchnote_gen.diff_stats.get_diff_stat")
def test_get_diff_stats_skips_none(mock_single):
    mock_single.side_effect = [DiffStat(sha="a"), None, DiffStat(sha="c")]
    results = get_diff_stats(["a", "b", "c"])
    assert len(results) == 2
    assert results[0].sha == "a"
    assert results[1].sha == "c"


def test_summarise_stats_empty():
    summary = summarise_stats([])
    assert summary["total_commits"] == 0
    assert summary["net_lines"] == 0


def test_summarise_stats_aggregates():
    stats = [
        DiffStat(sha="a", files_changed=1, insertions=10, deletions=2),
        DiffStat(sha="b", files_changed=3, insertions=5, deletions=5),
    ]
    summary = summarise_stats(stats)
    assert summary["total_commits"] == 2
    assert summary["total_files_changed"] == 4
    assert summary["total_insertions"] == 15
    assert summary["total_deletions"] == 7
    assert summary["net_lines"] == 8
