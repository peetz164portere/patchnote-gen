"""Tests for changelog_writer utilities."""

import pytest
from pathlib import Path

from patchnote_gen.changelog_writer import (
    write_output,
    prepend_to_file,
    append_to_file,
    stamp_filename,
    PREPEND_SEPARATOR,
)


CONTENT = "# Changelog\n\n- feat: something cool\n"


def test_write_output_to_file(tmp_path):
    out = tmp_path / "out.md"
    write_output(CONTENT, out)
    assert out.read_text() == CONTENT


def test_write_output_to_stdout(capsys):
    write_output("hello")
    captured = capsys.readouterr()
    assert "hello" in captured.out


def test_write_output_stdout_adds_newline(capsys):
    write_output("no newline at end")
    captured = capsys.readouterr()
    assert captured.out.endswith("\n")


def test_prepend_to_new_file(tmp_path):
    out = tmp_path / "CHANGELOG.md"
    prepend_to_file(CONTENT, out)
    assert out.read_text() == CONTENT


def test_prepend_to_existing_file(tmp_path):
    out = tmp_path / "CHANGELOG.md"
    existing = "# Old entry\n"
    out.write_text(existing)
    prepend_to_file(CONTENT, out)
    result = out.read_text()
    assert result.startswith(CONTENT)
    assert existing in result
    assert PREPEND_SEPARATOR in result


def test_append_to_new_file(tmp_path):
    out = tmp_path / "CHANGELOG.md"
    append_to_file(CONTENT, out)
    assert out.read_text() == CONTENT


def test_append_to_existing_file(tmp_path):
    out = tmp_path / "CHANGELOG.md"
    out.write_text("# Old\n")
    append_to_file(CONTENT, out)
    result = out.read_text()
    assert "# Old" in result
    assert CONTENT in result
    assert PREPEND_SEPARATOR in result


def test_stamp_filename_with_version():
    assert stamp_filename("CHANGELOG", "2.0.0") == "CHANGELOG-2.0.0.md"


def test_stamp_filename_without_version():
    from datetime import date
    today = date.today().isoformat()
    assert stamp_filename("CHANGELOG") == f"CHANGELOG-{today}.md"


def test_stamp_filename_custom_base():
    result = stamp_filename("RELEASE_NOTES", "0.1.0")
    assert result == "RELEASE_NOTES-0.1.0.md"
