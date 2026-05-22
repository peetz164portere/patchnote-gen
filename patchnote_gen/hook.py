"""Git hook installer for patchnote-gen.

Installs a commit-msg or post-commit hook into the current repo's
.git/hooks directory so changelogs can be auto-generated on commit.
"""

from __future__ import annotations

import os
import stat
from pathlib import Path

COMMIT_MSG_HOOK = """\
#!/usr/bin/env sh
# installed by patchnote-gen
set -e
patchnote-gen --since HEAD~1 --output CHANGELOG.md --prepend
"""

POST_COMMIT_HOOK = """\
#!/usr/bin/env sh
# installed by patchnote-gen
set -e
patchnote-gen --since HEAD~1 --output CHANGELOG.md --prepend
"""

HOOK_SCRIPTS = {
    "commit-msg": COMMIT_MSG_HOOK,
    "post-commit": POST_COMMIT_HOOK,
}


def _hooks_dir(repo_root: str | Path | None = None) -> Path:
    root = Path(repo_root) if repo_root else Path.cwd()
    return root / ".git" / "hooks"


def install_hook(hook_type: str = "post-commit", repo_root: str | Path | None = None) -> Path:
    """Write the hook script and make it executable. Returns the hook path."""
    if hook_type not in HOOK_SCRIPTS:
        raise ValueError(f"Unknown hook type '{hook_type}'. Choose from: {list(HOOK_SCRIPTS)}")

    hooks_dir = _hooks_dir(repo_root)
    if not hooks_dir.exists():
        raise FileNotFoundError(f"Hooks directory not found: {hooks_dir}. Is this a git repo?")

    hook_path = hooks_dir / hook_type

    if hook_path.exists():
        existing = hook_path.read_text()
        if "patchnote-gen" in existing:
            return hook_path  # already installed, skip
        # append to existing hook
        hook_path.write_text(existing.rstrip("\n") + "\n" + HOOK_SCRIPTS[hook_type])
    else:
        hook_path.write_text(HOOK_SCRIPTS[hook_type])

    # make executable
    current = hook_path.stat().st_mode
    hook_path.chmod(current | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return hook_path


def uninstall_hook(hook_type: str = "post-commit", repo_root: str | Path | None = None) -> bool:
    """Remove patchnote-gen lines from the hook. Returns True if anything was removed."""
    hook_path = _hooks_dir(repo_root) / hook_type
    if not hook_path.exists():
        return False

    lines = hook_path.read_text().splitlines(keepends=True)
    filtered = [l for l in lines if "patchnote-gen" not in l]
    if len(filtered) == len(lines):
        return False

    remaining = "".join(filtered).strip()
    if remaining:
        hook_path.write_text(remaining + "\n")
    else:
        hook_path.unlink()
    return True


def hook_status(hook_type: str = "post-commit", repo_root: str | Path | None = None) -> bool:
    """Return True if patchnote-gen hook is currently installed."""
    hook_path = _hooks_dir(repo_root) / hook_type
    if not hook_path.exists():
        return False
    return "patchnote-gen" in hook_path.read_text()
