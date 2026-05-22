"""Contributor statistics extracted from git commit history."""
from __future__ import annotations

from dataclasses import dataclass, field
from collections import defaultdict
from typing import List, Dict

from .git_parser import Commit


@dataclass
class ContributorStat:
    name: str
    email: str
    commit_count: int = 0
    types: Dict[str, int] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"{self.name} <{self.email}> ({self.commit_count} commits)"

    @property
    def top_type(self) -> str | None:
        """Return the most frequent commit type for this contributor."""
        if not self.types:
            return None
        return max(self.types, key=lambda t: self.types[t])


def collect_contributors(commits: List[Commit]) -> List[ContributorStat]:
    """Aggregate per-author statistics from a list of commits.

    Returns a list of ContributorStat sorted by commit count descending.
    """
    index: Dict[str, ContributorStat] = {}

    for commit in commits:
        author = getattr(commit, "author", None)
        email = getattr(commit, "author_email", "") or ""
        if not author:
            continue

        key = email.lower() if email else author.lower()
        if key not in index:
            index[key] = ContributorStat(name=author, email=email)

        stat = index[key]
        stat.commit_count += 1

        ctype = commit.commit_type or "other"
        stat.types[ctype] = stat.types.get(ctype, 0) + 1

    return sorted(index.values(), key=lambda s: s.commit_count, reverse=True)


def format_contributors(stats: List[ContributorStat], *, markdown: bool = True) -> str:
    """Render contributor stats as a markdown or plain-text table."""
    if not stats:
        return "No contributors found."

    if not markdown:
        lines = ["Contributors:", "-" * 40]
        for s in stats:
            lines.append(f"  {s.name} <{s.email}> — {s.commit_count} commits")
        return "\n".join(lines)

    header = "| Author | Email | Commits | Top Type |"
    sep = "| --- | --- | ---: | --- |"
    rows = [
        f"| {s.name} | {s.email} | {s.commit_count} | {s.top_type or '-'} |"
        for s in stats
    ]
    return "\n".join([header, sep] + rows)
