"""Full-text and field search across commit history."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional

from patchnote_gen.git_parser import Commit


@dataclass
class SearchQuery:
    text: Optional[str] = None
    types: List[str] = field(default_factory=list)
    scopes: List[str] = field(default_factory=list)
    authors: List[str] = field(default_factory=list)
    regex: bool = False
    case_sensitive: bool = False


@dataclass
class SearchResult:
    commit: Commit
    matched_fields: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        fields = ", ".join(self.matched_fields)
        return f"{self.commit.sha[:7]} [{fields}] {self.commit.message}"


def _text_matches(value: str, text: str, regex: bool, case_sensitive: bool) -> bool:
    if not case_sensitive:
        value = value.lower()
        text = text.lower()
    if regex:
        return bool(re.search(text, value))
    return text in value


def search_commits(
    commits: List[Commit],
    query: SearchQuery,
) -> List[SearchResult]:
    """Return commits matching *all* non-empty criteria in *query*."""
    results: List[SearchResult] = []

    for commit in commits:
        matched: List[str] = []

        if query.types:
            if commit.commit_type not in query.types:
                continue
            matched.append("type")

        if query.scopes:
            scope = (commit.scope or "").lower()
            if not any(s.lower() == scope for s in query.scopes):
                continue
            matched.append("scope")

        if query.authors:
            author = commit.author.lower()
            if not any(a.lower() in author for a in query.authors):
                continue
            matched.append("author")

        if query.text:
            hit = False
            for field_name, field_value in [
                ("message", commit.message),
                ("body", commit.body or ""),
            ]:
                if _text_matches(
                    field_value, query.text, query.regex, query.case_sensitive
                ):
                    matched.append(field_name)
                    hit = True
            if not hit:
                continue

        if not matched:
            matched.append("commit")

        results.append(SearchResult(commit=commit, matched_fields=matched))

    return results


def format_search_results(results: List[SearchResult]) -> str:
    if not results:
        return "No commits matched the search query."
    lines = [f"Found {len(results)} commit(s):", ""]
    lines.extend(str(r) for r in results)
    return "\n".join(lines)
