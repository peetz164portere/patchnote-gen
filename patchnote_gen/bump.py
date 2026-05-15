"""High-level version bump workflow for patchnote-gen CLI."""

from __future__ import annotations

from typing import Optional

from .git_parser import get_commits, commit_type
from .version_tagger import (
    Version,
    get_latest_tag,
    parse_version,
    suggest_next_version,
)


def collect_commit_types(since: Optional[str], until: str = "HEAD") -> list[str]:
    """Return a deduplicated list of commit types found in the range."""
    commits = get_commits(since=since, until=until)
    types = [commit_type(c) for c in commits if commit_type(c)]
    return list(dict.fromkeys(types))  # preserve order, deduplicate


def resolve_current_version(override: Optional[str] = None) -> Optional[Version]:
    """Return the current version from an override string or the latest git tag."""
    tag = override or get_latest_tag()
    if tag is None:
        return None
    return parse_version(tag)


def compute_next_version(
    since: Optional[str] = None,
    until: str = "HEAD",
    current_override: Optional[str] = None,
) -> Optional[tuple[Version, Version]]:
    """
    Compute (current, next) version tuple.

    Returns None if no current version can be determined.
    """
    current = resolve_current_version(current_override)
    if current is None:
        return None
    types = collect_commit_types(since=since, until=until)
    nxt = suggest_next_version(current, types)
    return current, nxt
