"""Collect and summarise per-commit diff statistics from git."""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class DiffStat:
    sha: str
    files_changed: int = 0
    insertions: int = 0
    deletions: int = 0
    files: List[str] = field(default_factory=list)

    @property
    def net_lines(self) -> int:
        return self.insertions - self.deletions

    def __str__(self) -> str:
        return (
            f"{self.files_changed} file(s) changed, "
            f"+{self.insertions} -{self.deletions}"
        )


def get_diff_stat(sha: str, repo_path: str = ".") -> Optional[DiffStat]:
    """Return a DiffStat for a single commit SHA."""
    try:
        result = subprocess.run(
            ["git", "show", "--stat", "--format=", sha],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError:
        return None

    lines = result.stdout.strip().splitlines()
    stat = DiffStat(sha=sha)

    for line in lines:
        # summary line: "3 files changed, 42 insertions(+), 7 deletions(-)"
        summary = re.match(
            r"\s*(\d+) files? changed"
            r"(?:,\s*(\d+) insertions?\(\+\))?"
            r"(?:,\s*(\d+) deletions?\(-\))?",
            line,
        )
        if summary:
            stat.files_changed = int(summary.group(1))
            stat.insertions = int(summary.group(2) or 0)
            stat.deletions = int(summary.group(3) or 0)
        elif line.strip() and not line.startswith("commit"):
            # file path lines look like " src/foo.py | 12 +++---"
            match = re.match(r"\s*(.+?)\s+\|", line)
            if match:
                stat.files.append(match.group(1).strip())

    return stat


def get_diff_stats(shas: List[str], repo_path: str = ".") -> List[DiffStat]:
    """Return DiffStat objects for a list of commit SHAs."""
    stats = []
    for sha in shas:
        s = get_diff_stat(sha, repo_path)
        if s is not None:
            stats.append(s)
    return stats


def summarise_stats(stats: List[DiffStat]) -> dict:
    """Aggregate a list of DiffStat into a summary dict."""
    return {
        "total_commits": len(stats),
        "total_files_changed": sum(s.files_changed for s in stats),
        "total_insertions": sum(s.insertions for s in stats),
        "total_deletions": sum(s.deletions for s in stats),
        "net_lines": sum(s.net_lines for s in stats),
    }
