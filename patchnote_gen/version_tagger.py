"""Version tagging utilities for patchnote-gen."""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from typing import Optional


@dataclass
class Version:
    major: int
    minor: int
    patch: int
    pre: Optional[str] = None

    def __str__(self) -> str:
        base = f"{self.major}.{self.minor}.{self.patch}"
        return f"{base}-{self.pre}" if self.pre else base

    def bump_major(self) -> "Version":
        return Version(self.major + 1, 0, 0)

    def bump_minor(self) -> "Version":
        return Version(self.major, self.minor + 1, 0)

    def bump_patch(self) -> "Version":
        return Version(self.major, self.minor, self.patch + 1)


_VERSION_RE = re.compile(
    r"^v?(\d+)\.(\d+)\.(\d+)(?:-([\w\.]+))?$"
)


def parse_version(tag: str) -> Optional[Version]:
    """Parse a semver string into a Version object."""
    m = _VERSION_RE.match(tag.strip())
    if not m:
        return None
    return Version(
        int(m.group(1)),
        int(m.group(2)),
        int(m.group(3)),
        m.group(4),
    )


def get_latest_tag() -> Optional[str]:
    """Return the most recent git tag reachable from HEAD, or None."""
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip() or None
    except subprocess.CalledProcessError:
        return None


def suggest_next_version(current: Version, commit_types: list[str]) -> Version:
    """Suggest the next version based on the types of commits since last tag."""
    if "breaking" in commit_types or "BREAKING CHANGE" in commit_types:
        return current.bump_major()
    if "feat" in commit_types:
        return current.bump_minor()
    return current.bump_patch()
