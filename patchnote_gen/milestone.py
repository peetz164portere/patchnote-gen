"""Milestone detection: identify notable commits that warrant release highlights."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .git_parser import Commit

BREAKING_MARKERS = ("BREAKING CHANGE", "BREAKING-CHANGE")
HIGHLIGHT_TYPES = {"feat", "fix", "perf"}


@dataclass
class Milestone:
    commit: Commit
    reason: str
    priority: int  # lower = more important

    def __str__(self) -> str:
        scope_part = f"({self.commit.scope})" if self.commit.scope else ""
        return f"[{self.reason}] {self.commit.commit_type}{scope_part}: {self.commit.message}"


def _is_breaking(commit: Commit) -> bool:
    """Return True if the commit body/footer signals a breaking change."""
    body = commit.raw_body if hasattr(commit, "raw_body") else ""
    for marker in BREAKING_MARKERS:
        if marker in (body or ""):
            return True
    if commit.commit_type and commit.commit_type.endswith("!"):
        return True
    return False


def detect_milestones(
    commits: List[Commit],
    extra_highlight_types: Optional[List[str]] = None,
) -> List[Milestone]:
    """Scan commits and return those considered milestones, ordered by priority."""
    highlight = HIGHLIGHT_TYPES | set(extra_highlight_types or [])
    milestones: List[Milestone] = []

    for commit in commits:
        if _is_breaking(commit):
            milestones.append(Milestone(commit=commit, reason="breaking", priority=0))
        elif commit.commit_type in highlight:
            priority = 1 if commit.commit_type == "feat" else 2
            milestones.append(Milestone(commit=commit, reason=commit.commit_type, priority=priority))

    milestones.sort(key=lambda m: m.priority)
    return milestones


def format_milestones(milestones: List[Milestone], title: str = "Release Highlights") -> str:
    """Render milestones as a Markdown section."""
    if not milestones:
        return ""
    lines = [f"## {title}\n"]
    for ms in milestones:
        scope_part = f" **({ms.commit.scope})**" if ms.commit.scope else ""
        badge = f"`{ms.reason.upper()}`"
        lines.append(f"- {badge}{scope_part} {ms.commit.message}")
    return "\n".join(lines) + "\n"
