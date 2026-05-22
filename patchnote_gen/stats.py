"""Aggregate statistics across a range of commits."""
from __future__ import annotations

from dataclasses import dataclass, field
from collections import Counter
from typing import List, Dict

from .git_parser import Commit


@dataclass
class CommitStats:
    total: int = 0
    by_type: Dict[str, int] = field(default_factory=dict)
    by_scope: Dict[str, int] = field(default_factory=dict)
    breaking: int = 0
    authors: Dict[str, int] = field(default_factory=dict)

    def summary(self) -> str:
        lines = [
            f"Total commits : {self.total}",
            f"Breaking changes: {self.breaking}",
        ]
        if self.by_type:
            lines.append("By type:")
            for t, n in sorted(self.by_type.items()):
                lines.append(f"  {t}: {n}")
        if self.by_scope:
            lines.append("By scope:")
            for s, n in sorted(self.by_scope.items()):
                lines.append(f"  {s}: {n}")
        if self.authors:
            lines.append("By author:")
            for a, n in sorted(self.authors.items(), key=lambda x: -x[1]):
                lines.append(f"  {a}: {n}")
        return "\n".join(lines)


def compute_stats(commits: List[Commit]) -> CommitStats:
    """Compute aggregate statistics from a list of Commit objects."""
    type_counter: Counter = Counter()
    scope_counter: Counter = Counter()
    author_counter: Counter = Counter()
    breaking = 0

    for c in commits:
        t = c.commit_type or "unknown"
        type_counter[t] += 1

        if c.scope:
            scope_counter[c.scope] += 1

        if hasattr(c, "author") and c.author:
            author_counter[c.author] += 1

        raw = c.raw if hasattr(c, "raw") else ""
        if "BREAKING CHANGE" in raw or (c.commit_type and c.commit_type.endswith("!")):
            breaking += 1

    return CommitStats(
        total=len(commits),
        by_type=dict(type_counter),
        by_scope=dict(scope_counter),
        breaking=breaking,
        authors=dict(author_counter),
    )
