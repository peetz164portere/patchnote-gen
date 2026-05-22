"""Compare two version ranges and summarize the diff between them."""

from dataclasses import dataclass, field
from typing import List, Optional

from .git_parser import Commit, get_commits
from .filter import partition_commits
from .bump import collect_commit_types


@dataclass
class CompareResult:
    from_ref: str
    to_ref: str
    commits: List[Commit] = field(default_factory=list)
    breaking: List[Commit] = field(default_factory=list)
    features: List[Commit] = field(default_factory=list)
    fixes: List[Commit] = field(default_factory=list)
    other: List[Commit] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.commits)

    @property
    def summary(self) -> str:
        parts = []
        if self.breaking:
            parts.append(f"{len(self.breaking)} breaking")
        if self.features:
            parts.append(f"{len(self.features)} feature(s)")
        if self.fixes:
            parts.append(f"{len(self.fixes)} fix(es)")
        if self.other:
            parts.append(f"{len(self.other)} other")
        if not parts:
            return "No changes."
        return ", ".join(parts) + f" across {self.total} commit(s)."


def compare_refs(
    from_ref: str,
    to_ref: str = "HEAD",
    repo_path: str = ".",
) -> CompareResult:
    """Fetch commits between two refs and partition them into categories."""
    since = from_ref
    commits = get_commits(repo_path=repo_path, since=since, until=to_ref)
    breaking, rest = partition_commits(commits)
    features = [c for c in rest if c.commit_type == "feat"]
    fixes = [c for c in rest if c.commit_type == "fix"]
    other = [c for c in rest if c.commit_type not in ("feat", "fix")]
    return CompareResult(
        from_ref=from_ref,
        to_ref=to_ref,
        commits=commits,
        breaking=breaking,
        features=features,
        fixes=fixes,
        other=other,
    )


def format_compare_result(result: CompareResult, verbose: bool = False) -> str:
    """Render a CompareResult as a human-readable string."""
    lines = [
        f"## Comparing {result.from_ref}..{result.to_ref}",
        f"Summary: {result.summary}",
    ]
    if verbose and result.commits:
        lines.append("")
        lines.append("### Commits")
        for c in result.commits:
            tag = f"[{c.commit_type}]" if c.commit_type else "[misc]"
            scope = f"({c.scope})" if c.scope else ""
            lines.append(f"  {tag}{scope} {c.message}")
    return "\n".join(lines)
