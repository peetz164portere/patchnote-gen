"""tag_summary.py – Summarise commits between two git tags."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .git_parser import Commit, get_commits
from .stats import compute_stats, CommitStats


@dataclass
class TagSummary:
    from_tag: str
    to_tag: str
    commits: List[Commit] = field(default_factory=list)
    stats: Optional[CommitStats] = None

    def __str__(self) -> str:  # pragma: no cover
        return format_tag_summary(self)


def build_tag_summary(from_tag: str, to_tag: str = "HEAD") -> TagSummary:
    """Collect commits between *from_tag* and *to_tag* and compute stats."""
    ref_range = f"{from_tag}..{to_tag}"
    commits = get_commits(since=None, until=None, ref_range=ref_range)
    stats = compute_stats(commits) if commits else None
    return TagSummary(from_tag=from_tag, to_tag=to_tag, commits=commits, stats=stats)


def format_tag_summary(summary: TagSummary) -> str:
    """Return a human-readable text summary for *summary*."""
    lines: List[str] = [
        f"## Changes from {summary.from_tag} → {summary.to_tag}",
        f"Total commits : {len(summary.commits)}",
    ]
    if summary.stats:
        s = summary.stats
        lines.append(f"Authors        : {len(s.by_author)}")
        if s.by_type:
            lines.append("By type:")
            for t, n in sorted(s.by_type.items(), key=lambda x: -x[1]):
                lines.append(f"  {t:<12} {n}")
        if s.by_scope:
            lines.append("By scope:")
            for sc, n in sorted(s.by_scope.items(), key=lambda x: -x[1]):
                lines.append(f"  {sc:<12} {n}")
    return "\n".join(lines)
