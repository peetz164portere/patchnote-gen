"""Tests for patchnote_gen.hook_cli"""

from pathlib import Path

import pytest

from patchnote_gen.hook_cli import build_hook_parser, main


@pytest.fixture()
def fake_repo(tmp_path: Path) -> Path:
    hooks_dir = tmp_path / ".git" / "hooks"
    hooks_dir.mkdir(parents=True)
    return tmp_path


def test_build_parser_install_defaults():
    parser = build_hook_parser()
    args = parser.parse_args(["install"])
    assert args.command == "install"
    assert args.hook_type == "post-commit"
    assert args.repo is None


def test_build_parser_install_commit_msg():
    parser = build_hook_parser()
    args = parser.parse_args(["install", "--type", "commit-msg"])
    assert args.hook_type == "commit-msg"


def test_build_parser_status_defaults():
    parser = build_hook_parser()
    args = parser.parse_args(["status"])
    assert args.command == "status"


def test_main_install_creates_hook(fake_repo):
    rc = main(["install", "--repo", str(fake_repo)])
    assert rc == 0
    hook_path = fake_repo / ".git" / "hooks" / "post-commit"
    assert hook_path.exists()


def test_main_install_prints_path(fake_repo, capsys):
    main(["install", "--repo", str(fake_repo)])
    out = capsys.readouterr().out
    assert "Installed" in out
    assert "post-commit" in out


def test_main_status_not_installed_returns_1(fake_repo):
    rc = main(["status", "--repo", str(fake_repo)])
    assert rc == 1


def test_main_status_installed_returns_0(fake_repo):
    main(["install", "--repo", str(fake_repo)])
    rc = main(["status", "--repo", str(fake_repo)])
    assert rc == 0


def test_main_status_output(fake_repo, capsys):
    main(["install", "--repo", str(fake_repo)])
    main(["status", "--repo", str(fake_repo)])
    out = capsys.readouterr().out
    assert "installed" in out


def test_main_uninstall_returns_0(fake_repo):
    main(["install", "--repo", str(fake_repo)])
    rc = main(["uninstall", "--repo", str(fake_repo)])
    assert rc == 0


def test_main_uninstall_not_installed_message(fake_repo, capsys):
    main(["uninstall", "--repo", str(fake_repo)])
    out = capsys.readouterr().out
    assert "not installed" in out


def test_main_install_no_git_dir_returns_2(tmp_path):
    rc = main(["install", "--repo", str(tmp_path)])
    assert rc == 2
