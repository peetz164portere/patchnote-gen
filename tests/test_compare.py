"""Tests for patchnote_gen.compare."""

from unittest.mock import patch

import pytest

from patchnote_gen.git_parser import Commit
from patchnote_gen.compare import CompareResult, compare_refs, format_compare_result


def _commit(sha, ctype, scope=None, msg="some change", breaking=False):
    body = "BREAKING CHANGE: yes" if breaking else ""
    raw = f"{sha} {ctype}({'(' + scope + ')' if scope else ''}): {msg}"
    return Commit(sha=sha, raw_message=raw, body=body)


@pytest.fixture
def sample_result():
    breaking = _commit("aaa", "feat", breaking=True, msg="remove old API")
    feat = _commit("bbb", "feat", scope="auth", msg="add OAuth")
    fix = _commit("ccc", "fix", msg="null pointer")
    chore = _commit("ddd", "chore", msg="update deps")
    return CompareResult(
        from_ref="v1.0.0",
        to_ref="v2.0.0",
        commits=[breaking, feat, fix, chore],
        breaking=[breaking],
        features=[feat],
        fixes=[fix],
        other=[chore],
    )


def test_compare_result_total(sample_result):
    assert sample_result.total == 4


def test_compare_result_summary_all_categories(sample_result):
    s = sample_result.summary
    assert "breaking" in s
    assert "feature" in s
    assert "fix" in s
    assert "other" in s


def test_compare_result_summary_empty():
    result = CompareResult(from_ref="v1", to_ref="v2")
    assert result.summary == "No changes."


def test_format_compare_result_header(sample_result):
    output = format_compare_result(sample_result)
    assert "v1.0.0..v2.0.0" in output
    assert "Summary:" in output


def test_format_compare_result_verbose(sample_result):
    output = format_compare_result(sample_result, verbose=True)
    assert "### Commits" in output
    assert "[feat]" in output or "[fix]" in output


def test_format_compare_result_not_verbose_no_commit_list(sample_result):
    output = format_compare_result(sample_result, verbose=False)
    assert "### Commits" not in output


@patch("patchnote_gen.compare.get_commits")
@patch("patchnote_gen.compare.partition_commits")
def test_compare_refs_partitions_correctly(mock_partition, mock_get):
    feat = _commit("e1", "feat", msg="new thing")
    fix = _commit("e2", "fix", msg="broken thing")
    chore = _commit("e3", "chore", msg="cleanup")
    mock_get.return_value = [feat, fix, chore]
    mock_partition.return_value = ([], [feat, fix, chore])

    result = compare_refs("v1.0", "v1.1")

    assert result.total == 3
    assert len(result.features) == 1
    assert len(result.fixes) == 1
    assert len(result.other) == 1


@patch("patchnote_gen.compare.get_commits")
@patch("patchnote_gen.compare.partition_commits")
def test_compare_refs_breaking_separated(mock_partition, mock_get):
    b = _commit("x1", "feat", breaking=True, msg="drop support")
    mock_get.return_value = [b]
    mock_partition.return_value = ([b], [])

    result = compare_refs("v2.0", "v3.0")
    assert len(result.breaking) == 1
    assert result.total == 1
