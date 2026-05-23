"""Detect and report reverted commits in a commit range."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .git_parser import Commit


@dataclass
class RevertEntry:
    """A commit that reverts a previous commit."""

    reverting: Commit
    target_sha: Optional[str]  # SHA mentioned in the revert message, if any

    def __str__(self) -> str:
        sha = self.target_sha or "unknown"
        return f"revert {self.reverting.hash[:7]}: reverts {sha[:7]} — {self.reverting.message}"


@dataclass
class RevertReport:
    reverts: List[RevertEntry] = field(default_factory=list)
    since: str = ""
    until: str = ""

    @property
    def total(self) -> int:
        return len(self.reverts)

    def __str__(self) -> str:
        if not self.reverts:
            return "No reverts found."
        lines = [f"Reverts ({self.total}):"] + [f"  {e}" for e in self.reverts]
        return "\n".join(lines)


def _extract_target_sha(message: str) -> Optional[str]:
    """Try to pull a 7-40 char hex SHA from a revert commit message."""
    import re

    # Matches 'This reverts commit <sha>.' or bare SHA mentions
    patterns = [
        r"This reverts commit ([0-9a-f]{7,40})",
        r"reverts?\s+([0-9a-f]{7,40})",
    ]
    for pat in patterns:
        m = re.search(pat, message, re.IGNORECASE)
        if m:
            return m.group(1)
    return None


def collect_reverts(commits: List[Commit]) -> List[RevertEntry]:
    """Return a RevertEntry for every commit whose type is 'revert'."""
    entries: List[RevertEntry] = []
    for commit in commits:
        if commit.commit_type == "revert":
            sha = _extract_target_sha(commit.raw_message if hasattr(commit, "raw_message") else commit.message)
            entries.append(RevertEntry(reverting=commit, target_sha=sha))
    return entries


def build_revert_report(
    commits: List[Commit],
    since: str = "",
    until: str = "",
) -> RevertReport:
    return RevertReport(
        reverts=collect_reverts(commits),
        since=since,
        until=until,
    )


def format_revert_report(report: RevertReport) -> str:
    return str(report)
