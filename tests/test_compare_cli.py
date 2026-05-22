"""Tests for patchnote_gen.compare_cli."""

import json
from unittest.mock import patch, MagicMock

import pytest

from patchnote_gen.compare import CompareResult
from patchnote_gen.compare_cli import build_compare_parser, main
from patchnote_gen.git_parser import Commit


def _make_result(n_commits=2, n_feat=1, n_fix=1, n_breaking=0, n_other=0):
    commits = [MagicMock(spec=Commit) for _ in range(n_commits)]
    return CompareResult(
        from_ref="v1.0.0",
        to_ref="HEAD",
        commits=commits,
        breaking=commits[:n_breaking],
        features=commits[:n_feat],
        fixes=commits[:n_fix],
        other=commits[:n_other],
    )


def test_build_compare_parser_defaults():
    parser = build_compare_parser()
    args = parser.parse_args(["v1.0.0"])
    assert args.from_ref == "v1.0.0"
    assert args.to_ref == "HEAD"
    assert args.repo == "."
    assert args.verbose is False
    assert args.json is False


def test_build_compare_parser_all_flags():
    parser = build_compare_parser()
    args = parser.parse_args(["v1.0", "v2.0", "--repo", "/tmp/repo", "-v", "--json"])
    assert args.from_ref == "v1.0"
    assert args.to_ref == "v2.0"
    assert args.repo == "/tmp/repo"
    assert args.verbose is True
    assert args.json is True


@patch("patchnote_gen.compare_cli.compare_refs")
def test_main_no_commits_returns_1(mock_compare, capsys):
    mock_compare.return_value = CompareResult(from_ref="v1", to_ref="HEAD")
    rc = main(["v1"])
    assert rc == 1
    captured = capsys.readouterr()
    assert "No commits" in captured.err


@patch("patchnote_gen.compare_cli.compare_refs")
def test_main_prints_summary(mock_compare, capsys):
    mock_compare.return_value = _make_result()
    rc = main(["v1.0.0"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "v1.0.0" in captured.out


@patch("patchnote_gen.compare_cli.compare_refs")
def test_main_json_output(mock_compare, capsys):
    mock_compare.return_value = _make_result()
    rc = main(["v1.0.0", "--json"])
    assert rc == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "from_ref" in data
    assert "total" in data
    assert "summary" in data


@patch("patchnote_gen.compare_cli.compare_refs")
def test_main_verbose_flag_passed(mock_compare, capsys):
    mock_compare.return_value = _make_result()
    rc = main(["v1.0.0", "-v"])
    assert rc == 0
