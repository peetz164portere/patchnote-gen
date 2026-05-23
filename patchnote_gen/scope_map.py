"""scope_map.py – Build a mapping of scopes to commits and related utilities."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .git_parser import Commit


@dataclass
class ScopeEntry:
    scope: str
    commits: List[Commit] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.commits)

    @property
    def authors(self) -> List[str]:
        seen: set = set()
        result = []
        for c in self.commits:
            if c.author not in seen:
                seen.add(c.author)
                result.append(c.author)
        return result

    @property
    def types(self) -> List[str]:
        seen: set = set()
        result = []
        for c in self.commits:
            t = c.commit_type
            if t and t not in seen:
                seen.add(t)
                result.append(t)
        return result

    def __str__(self) -> str:
        types_str = ", ".join(self.types) if self.types else "misc"
        return f"{self.scope} ({self.count} commit{'s' if self.count != 1 else ''}, types: {types_str})"


def build_scope_map(commits: List[Commit]) -> Dict[str, ScopeEntry]:
    """Group commits by scope. Commits without a scope are filed under '(none)'."""
    mapping: Dict[str, ScopeEntry] = defaultdict(lambda: ScopeEntry(scope=""))
    for commit in commits:
        key = commit.scope.strip().lower() if commit.scope else "(none)"
        if mapping[key].scope == "":
            mapping[key].scope = key
        mapping[key].commits.append(commit)
    return dict(mapping)


def top_scopes(scope_map: Dict[str, ScopeEntry], n: int = 5) -> List[ScopeEntry]:
    """Return the n most active scopes sorted by commit count descending."""
    return sorted(scope_map.values(), key=lambda e: e.count, reverse=True)[:n]


def format_scope_map(
    scope_map: Dict[str, ScopeEntry],
    limit: Optional[int] = None,
) -> str:
    """Render a human-readable summary of the scope map."""
    entries = sorted(scope_map.values(), key=lambda e: e.count, reverse=True)
    if limit is not None:
        entries = entries[:limit]
    if not entries:
        return "No scoped commits found."
    lines = ["Scope breakdown:", ""]
    for entry in entries:
        lines.append(f"  {entry}")
        for author in entry.authors:
            lines.append(f"    - {author}")
    return "\n".join(lines)
