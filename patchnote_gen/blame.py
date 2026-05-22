"""Blame analysis: map commit authors to changed files."""
from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .git_parser import Commit


@dataclass
class BlameEntry:
    author: str
    files_touched: List[str] = field(default_factory=list)
    commit_count: int = 0

    def __str__(self) -> str:  # pragma: no cover
        files = len(self.files_touched)
        return f"{self.author}: {self.commit_count} commit(s), {files} file(s) touched"


def _files_for_commit(sha: str) -> List[str]:
    """Return list of files changed in a given commit."""
    try:
        result = subprocess.run(
            ["git", "diff-tree", "--no-commit-id", "-r", "--name-only", sha],
            capture_output=True,
            text=True,
            check=True,
        )
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]
    except subprocess.CalledProcessError:
        return []


def collect_blame(commits: List[Commit]) -> Dict[str, BlameEntry]:
    """Aggregate per-author file touch data across commits."""
    blame: Dict[str, BlameEntry] = {}
    for commit in commits:
        author = commit.author
        if author not in blame:
            blame[author] = BlameEntry(author=author)
        entry = blame[author]
        entry.commit_count += 1
        for f in _files_for_commit(commit.sha):
            if f not in entry.files_touched:
                entry.files_touched.append(f)
    return blame


def format_blame(blame: Dict[str, BlameEntry], top_n: Optional[int] = None) -> str:
    """Render blame report as a Markdown table."""
    rows = sorted(blame.values(), key=lambda e: e.commit_count, reverse=True)
    if top_n is not None:
        rows = rows[:top_n]
    if not rows:
        return "_No blame data available._"
    lines = [
        "| Author | Commits | Files Touched |",
        "|--------|---------|---------------|",
    ]
    for entry in rows:
        lines.append(f"| {entry.author} | {entry.commit_count} | {len(entry.files_touched)} |")
    return "\n".join(lines)
