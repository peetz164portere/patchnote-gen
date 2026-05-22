"""Filtering utilities for commit lists."""

from __future__ import annotations

from typing import List, Optional

from patchnote_gen.git_parser import Commit


def filter_commits(
    commits: List[Commit],
    include_types: Optional[List[str]] = None,
    exclude_types: Optional[List[str]] = None,
    scope: Optional[str] = None,
    breaking_only: bool = False,
) -> List[Commit]:
    """Return a filtered subset of commits based on criteria.

    Args:
        commits: Full list of commits to filter.
        include_types: If provided, only keep commits whose type is in this list.
        exclude_types: If provided, drop commits whose type is in this list.
        scope: If provided, only keep commits matching this scope (case-insensitive).
        breaking_only: If True, only keep commits marked as breaking changes.

    Returns:
        Filtered list of Commit objects.
    """
    result = commits

    if include_types is not None:
        result = [c for c in result if c.commit_type in include_types]

    if exclude_types is not None:
        result = [c for c in result if c.commit_type not in exclude_types]

    if scope is not None:
        result = [c for c in result if (c.scope or "").lower() == scope.lower()]

    if breaking_only:
        result = [c for c in result if _is_breaking(c)]

    return result


def _is_breaking(commit: Commit) -> bool:
    """Detect breaking change markers in a commit."""
    raw = commit.message or ""
    # Conventional commits mark breaking changes with '!' after type/scope
    # or with a 'BREAKING CHANGE:' footer.
    if "BREAKING CHANGE" in raw:
        return True
    # Check the raw subject line stored on the commit object if available
    subject = getattr(commit, "_raw", raw)
    return "!" in subject.split(":")[0] if ":" in subject else False


def partition_commits(
    commits: List[Commit],
    include_types: Optional[List[str]] = None,
) -> tuple[List[Commit], List[Commit]]:
    """Split commits into matched and unmatched groups.

    Args:
        commits: Full list of commits to partition.
        include_types: Commit types to match. Commits whose type is in this
            list go into the first returned list; all others go into the second.
            If *None*, all commits are placed in the matched list.

    Returns:
        A tuple of ``(matched, unmatched)`` commit lists.
    """
    if include_types is None:
        return list(commits), []

    matched = [c for c in commits if c.commit_type in include_types]
    unmatched = [c for c in commits if c.commit_type not in include_types]
    return matched, unmatched
