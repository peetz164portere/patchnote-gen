"""Weekly/periodic digest summarising commit activity across a date range."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import List, Dict

from .git_parser import Commit
from .stats import compute_stats
from .milestone import detect_milestones, format_milestones
from .contributor import collect_contributors, format_contributors


@dataclass
class DigestReport:
    """Aggregated digest for a period."""

    since: str
    until: str
    total_commits: int
    by_type: Dict[str, int] = field(default_factory=dict)
    highlights: List[str] = field(default_factory=list)
    top_contributors: List[str] = field(default_factory=list)

    def __str__(self) -> str:  # pragma: no cover
        return format_digest(self)


def build_digest(commits: List[Commit], since: str, until: str) -> DigestReport:
    """Build a DigestReport from a list of commits and a date range."""
    stats = compute_stats(commits)
    milestones = detect_milestones(commits)
    contributors = collect_contributors(commits)

    highlights = [str(m) for m in milestones]
    top = [str(c) for c in contributors[:5]]

    return DigestReport(
        since=since,
        until=until,
        total_commits=stats.total,
        by_type=dict(stats.by_type),
        highlights=highlights,
        top_contributors=top,
    )


def format_digest(report: DigestReport) -> str:
    """Render a DigestReport as a Markdown string."""
    lines: List[str] = [
        f"## Digest: {report.since} → {report.until}",
        "",
        f"**Total commits:** {report.total_commits}",
        "",
    ]

    if report.by_type:
        lines.append("### Breakdown by type")
        for t, count in sorted(report.by_type.items(), key=lambda x: -x[1]):
            lines.append(f"- `{t}`: {count}")
        lines.append("")

    if report.highlights:
        lines.append("### Highlights")
        for h in report.highlights:
            lines.append(f"- {h}")
        lines.append("")

    if report.top_contributors:
        lines.append("### Top contributors")
        for c in report.top_contributors:
            lines.append(f"- {c}")
        lines.append("")

    return "\n".join(lines)
