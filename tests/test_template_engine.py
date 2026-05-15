"""Tests for the template engine module."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock

from patchnote_gen.git_parser import Commit
from patchnote_gen.template_engine import (
    TemplateConfig,
    group_commits,
    render_markdown,
    render_from_template_file,
)


@pytest.fixture
def sample_commits():
    return [
        Commit(hash="abc1234def", type="feat", scope="auth", message="add login support", raw="feat(auth): add login support"),
        Commit(hash="bcd2345efg", type="fix", scope=None, message="resolve null pointer", raw="fix: resolve null pointer"),
        Commit(hash="cde3456fgh", type="feat", scope="ui", message="new dashboard layout", raw="feat(ui): new dashboard layout"),
        Commit(hash="def4567ghi", type="chore", scope=None, message="update dependencies", raw="chore: update dependencies"),
    ]


@pytest.fixture
def default_config():
    return TemplateConfig(title="My Changelog", version="1.2.0", date="2024-01-15")


def test_group_commits_by_type(sample_commits, default_config):
    groups = group_commits(sample_commits, default_config)
    assert "Features" in groups
    assert "Bug Fixes" in groups
    assert "Chores" in groups
    assert len(groups["Features"]) == 2
    assert len(groups["Bug Fixes"]) == 1


def test_group_commits_unknown_type(default_config):
    commit = Commit(hash="aaa111bbb", type="unknown", scope=None, message="something weird", raw="unknown: something weird")
    groups = group_commits([commit], default_config)
    assert "unknown" in groups


def test_render_markdown_header(sample_commits, default_config):
    output = render_markdown(sample_commits, default_config)
    assert "# My Changelog" in output
    assert "1.2.0" in output
    assert "2024-01-15" in output


def test_render_markdown_contains_commits(sample_commits, default_config):
    output = render_markdown(sample_commits, default_config)
    assert "add login support" in output
    assert "resolve null pointer" in output
    assert "abc1234" in output


def test_render_markdown_scope_bolded(sample_commits, default_config):
    output = render_markdown(sample_commits, default_config)
    assert "**auth**" in output
    assert "**ui**" in output


def test_render_markdown_no_grouping(sample_commits):
    config = TemplateConfig(title="Flat Log", group_by_type=False)
    output = render_markdown(sample_commits, config)
    assert "## Changes" in output
    assert "## Features" not in output


def test_render_from_template_file(sample_commits, default_config, tmp_path):
    template = tmp_path / "changelog.tpl"
    template.write_text("# {{title}} {{version}}\n\n{{sections}}")
    output = render_from_template_file(sample_commits, template, default_config)
    assert "My Changelog" in output
    assert "1.2.0" in output
    assert "Features" in output or "feat" in output.lower()


def test_render_markdown_no_version():
    config = TemplateConfig(title="Simple Log")
    commits = [Commit(hash="fff999eee", type="fix", scope=None, message="hotfix", raw="fix: hotfix")]
    output = render_markdown(commits, config)
    assert "Simple Log" in output
    assert "None" not in output
