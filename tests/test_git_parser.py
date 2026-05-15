"""Tests for the git_parser module."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from patchnote_gen.git_parser import Commit, get_commits


@pytest.fixture
def sample_commit():
    return Commit(
        hash="abc123def456",
        short_hash="abc123",
        author="Jane Dev",
        email="jane@example.com",
        date=datetime(2024, 1, 15, 10, 30, 0),
        subject="feat(auth): add OAuth2 login support",
        body="Implements Google and GitHub OAuth providers.",
    )


def test_commit_type_extraction(sample_commit):
    assert sample_commit.commit_type == "feat"


def test_commit_scope_extraction(sample_commit):
    assert sample_commit.scope == "auth"


def test_commit_message_extraction(sample_commit):
    assert sample_commit.message == "add OAuth2 login support"


def test_commit_no_conventional_format():
    c = Commit(
        hash="aaa", short_hash="aaa", author="Dev", email="d@d.com",
        date=datetime.now(), subject="fixed a bug"
    )
    assert c.commit_type is None
    assert c.scope is None
    assert c.message == "fixed a bug"


def test_commit_type_no_scope():
    c = Commit(
        hash="bbb", short_hash="bbb", author="Dev", email="d@d.com",
        date=datetime.now(), subject="fix: resolve null pointer"
    )
    assert c.commit_type == "fix"
    assert c.scope is None
    assert c.message == "resolve null pointer"


@patch("patchnote_gen.git_parser.subprocess.run")
def test_get_commits_parses_output(mock_run):
    sep = "||COMMIT_SEP||"
    fake_output = (
        f"abc123def456{sep}abc123{sep}Jane Dev{sep}jane@example.com{sep}"
        f"2024-01-15T10:30:00+00:00{sep}feat: initial commit{sep}body text{sep}END"
    )
    mock_run.return_value = MagicMock(stdout=fake_output, returncode=0)

    commits = get_commits()
    assert len(commits) == 1
    assert commits[0].short_hash == "abc123"
    assert commits[0].commit_type == "feat"
    assert commits[0].message == "initial commit"


@patch("patchnote_gen.git_parser.subprocess.run")
def test_get_commits_empty_repo(mock_run):
    mock_run.return_value = MagicMock(stdout="", returncode=0)
    commits = get_commits()
    assert commits == []


@patch("patchnote_gen.git_parser.subprocess.run")
def test_get_commits_since_tag_passes_arg(mock_run):
    mock_run.return_value = MagicMock(stdout="", returncode=0)
    get_commits(since_tag="v1.0.0")
    call_args = mock_run.call_args[0][0]
    assert "v1.0.0..HEAD" in call_args
