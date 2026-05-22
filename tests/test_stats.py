"""Tests for patchnote_gen.stats and stats_cli."""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

import pytest

from patchnote_gen.stats import CommitStats, compute_stats


def _commit(ctype="feat", scope=None, author="alice", raw=""):
    return SimpleNamespace(
        commit_type=ctype,
        scope=scope,
        author=author,
        raw=raw,
        message="msg",
    )


@pytest.fixture()
def sample_commits():
    return [
        _commit("feat", "auth", "alice"),
        _commit("fix", "auth", "bob"),
        _commit("feat", None, "alice"),
        _commit("chore", "ci", "charlie"),
        _commit("feat", "api", "alice", raw="BREAKING CHANGE: removed endpoint"),
    ]


def test_compute_stats_total(sample_commits):
    s = compute_stats(sample_commits)
    assert s.total == 5


def test_compute_stats_by_type(sample_commits):
    s = compute_stats(sample_commits)
    assert s.by_type["feat"] == 3
    assert s.by_type["fix"] == 1
    assert s.by_type["chore"] == 1


def test_compute_stats_by_scope(sample_commits):
    s = compute_stats(sample_commits)
    assert s.by_scope["auth"] == 2
    assert s.by_scope["ci"] == 1
    assert s.by_scope["api"] == 1
    assert "" not in s.by_scope


def test_compute_stats_breaking(sample_commits):
    s = compute_stats(sample_commits)
    assert s.breaking == 1


def test_compute_stats_authors(sample_commits):
    s = compute_stats(sample_commits)
    assert s.authors["alice"] == 3
    assert s.authors["bob"] == 1


def test_compute_stats_empty():
    s = compute_stats([])
    assert s.total == 0
    assert s.breaking == 0
    assert s.by_type == {}


def test_summary_contains_total(sample_commits):
    s = compute_stats(sample_commits)
    summary = s.summary()
    assert "5" in summary
    assert "feat" in summary


def test_stats_cli_no_commits_returns_1():
    from patchnote_gen.stats_cli import main

    with patch("patchnote_gen.stats_cli.get_commits", return_value=[]):
        assert main([]) == 1


def test_stats_cli_prints_summary(sample_commits, capsys):
    from patchnote_gen.stats_cli import main

    with patch("patchnote_gen.stats_cli.get_commits", return_value=sample_commits):
        rc = main([])
    assert rc == 0
    out = capsys.readouterr().out
    assert "Total commits" in out


def test_stats_cli_json_output(sample_commits, capsys):
    import json
    from patchnote_gen.stats_cli import main

    with patch("patchnote_gen.stats_cli.get_commits", return_value=sample_commits):
        rc = main(["--json"])
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data["total"] == 5
    assert "by_type" in data
