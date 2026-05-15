"""Tests for the CLI module."""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from patchnote_gen.cli import build_parser, main
from patchnote_gen.git_parser import Commit


SAMPLE_COMMITS = [
    Commit(hash="abc1234", raw="feat(auth): add login support", author="Alice", date="2024-01-01"),
    Commit(hash="def5678", raw="fix: resolve null pointer", author="Bob", date="2024-01-02"),
]


def test_build_parser_defaults():
    parser = build_parser()
    args = parser.parse_args([])
    assert args.since is None
    assert args.until == "HEAD"
    assert args.output is None
    assert args.template is None
    assert args.config == "patchnote.toml"
    assert args.init is False


def test_build_parser_since_until():
    parser = build_parser()
    args = parser.parse_args(["--since", "v1.0.0", "--until", "v2.0.0"])
    assert args.since == "v1.0.0"
    assert args.until == "v2.0.0"


def test_build_parser_output_short():
    parser = build_parser()
    args = parser.parse_args(["-o", "CHANGELOG.md"])
    assert args.output == "CHANGELOG.md"


@patch("patchnote_gen.cli.save_config")
@patch("patchnote_gen.cli.load_config")
def test_init_flag_writes_config(mock_load, mock_save, capsys):
    mock_load.return_value = MagicMock()
    result = main(["--init", "--config", "test.toml"])
    assert result == 0
    mock_save.assert_called_once()
    captured = capsys.readouterr()
    assert "test.toml" in captured.out


@patch("patchnote_gen.cli.get_commits", return_value=[])
@patch("patchnote_gen.cli.load_config")
def test_main_no_commits_returns_1(mock_load, mock_commits, capsys):
    mock_load.return_value = MagicMock(version="1.0.0")
    result = main([])
    assert result == 1


@patch("patchnote_gen.cli.render_markdown", return_value="# Changelog\n")
@patch("patchnote_gen.cli.get_commits", return_value=SAMPLE_COMMITS)
@patch("patchnote_gen.cli.load_config")
def test_main_prints_to_stdout(mock_load, mock_commits, mock_render, capsys):
    mock_load.return_value = MagicMock(version="1.0.0")
    result = main([])
    assert result == 0
    captured = capsys.readouterr()
    assert "Changelog" in captured.out


@patch("patchnote_gen.cli.render_markdown", return_value="# Changelog\n")
@patch("patchnote_gen.cli.get_commits", return_value=SAMPLE_COMMITS)
@patch("patchnote_gen.cli.load_config")
def test_main_writes_to_file(mock_load, mock_commits, mock_render, tmp_path, capsys):
    mock_load.return_value = MagicMock(version="1.0.0")
    out_file = tmp_path / "CHANGELOG.md"
    result = main(["-o", str(out_file)])
    assert result == 0
    assert out_file.read_text() == "# Changelog\n"


@patch("patchnote_gen.cli.render_from_template_file", return_value="custom output")
@patch("patchnote_gen.cli.get_commits", return_value=SAMPLE_COMMITS)
@patch("patchnote_gen.cli.load_config")
def test_main_uses_custom_template(mock_load, mock_commits, mock_render, tmp_path, capsys):
    mock_load.return_value = MagicMock(version="1.0.0")
    tmpl = tmp_path / "tmpl.md.j2"
    tmpl.write_text("{{ commits }}")
    result = main(["--template", str(tmpl)])
    assert result == 0
    mock_render.assert_called_once()
