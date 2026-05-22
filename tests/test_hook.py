"""Tests for patchnote_gen.hook"""

import stat
from pathlib import Path

import pytest

from patchnote_gen.hook import install_hook, uninstall_hook, hook_status


@pytest.fixture()
def fake_repo(tmp_path: Path) -> Path:
    hooks_dir = tmp_path / ".git" / "hooks"
    hooks_dir.mkdir(parents=True)
    return tmp_path


def test_install_hook_creates_file(fake_repo):
    hook_path = install_hook("post-commit", repo_root=fake_repo)
    assert hook_path.exists()
    assert "patchnote-gen" in hook_path.read_text()


def test_install_hook_is_executable(fake_repo):
    hook_path = install_hook("post-commit", repo_root=fake_repo)
    mode = hook_path.stat().st_mode
    assert mode & stat.S_IXUSR


def test_install_hook_idempotent(fake_repo):
    install_hook("post-commit", repo_root=fake_repo)
    install_hook("post-commit", repo_root=fake_repo)
    content = (fake_repo / ".git" / "hooks" / "post-commit").read_text()
    assert content.count("patchnote-gen") == 1


def test_install_hook_appends_to_existing(fake_repo):
    hook_path = fake_repo / ".git" / "hooks" / "post-commit"
    hook_path.write_text("#!/usr/bin/env sh\necho hello\n")
    install_hook("post-commit", repo_root=fake_repo)
    content = hook_path.read_text()
    assert "echo hello" in content
    assert "patchnote-gen" in content


def test_install_hook_commit_msg_type(fake_repo):
    hook_path = install_hook("commit-msg", repo_root=fake_repo)
    assert hook_path.name == "commit-msg"
    assert "patchnote-gen" in hook_path.read_text()


def test_install_hook_unknown_type_raises(fake_repo):
    with pytest.raises(ValueError, match="Unknown hook type"):
        install_hook("pre-push", repo_root=fake_repo)


def test_install_hook_no_git_dir_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        install_hook("post-commit", repo_root=tmp_path)


def test_uninstall_hook_removes_content(fake_repo):
    install_hook("post-commit", repo_root=fake_repo)
    removed = uninstall_hook("post-commit", repo_root=fake_repo)
    assert removed is True
    hook_path = fake_repo / ".git" / "hooks" / "post-commit"
    assert not hook_path.exists()


def test_uninstall_hook_preserves_other_content(fake_repo):
    hook_path = fake_repo / ".git" / "hooks" / "post-commit"
    hook_path.write_text("#!/usr/bin/env sh\necho hello\n")
    install_hook("post-commit", repo_root=fake_repo)
    uninstall_hook("post-commit", repo_root=fake_repo)
    assert hook_path.exists()
    assert "echo hello" in hook_path.read_text()
    assert "patchnote-gen" not in hook_path.read_text()


def test_uninstall_hook_returns_false_when_not_installed(fake_repo):
    result = uninstall_hook("post-commit", repo_root=fake_repo)
    assert result is False


def test_hook_status_true_when_installed(fake_repo):
    install_hook("post-commit", repo_root=fake_repo)
    assert hook_status("post-commit", repo_root=fake_repo) is True


def test_hook_status_false_when_not_installed(fake_repo):
    assert hook_status("post-commit", repo_root=fake_repo) is False
