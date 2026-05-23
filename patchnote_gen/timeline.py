"""Timeline: group commits by time period (day, week, month)."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Literal

from .git_parser import Commit

Period = Literal["day", "week", "month"]


@dataclass
class TimelineBucket:
    label: str
    commits: List[Commit] = field(default_factory=list)

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.label} ({len(self.commits)} commits)"

    @property
    def count(self) -> int:
        return len(self.commits)


@dataclass
class TimelineReport:
    period: Period
    buckets: List[TimelineBucket]

    @property
    def total(self) -> int:
        return sum(b.count for b in self.buckets)

    def summary(self) -> str:
        lines = [f"Timeline ({self.period}): {self.total} commits across {len(self.buckets)} bucket(s)"]
        for bucket in self.buckets:
            lines.append(f"  {bucket.label}: {bucket.count}")
        return "\n".join(lines)


def _bucket_label(ts: datetime, period: Period) -> str:
    """Return a string label for the given datetime and period."""
    if period == "day":
        return ts.strftime("%Y-%m-%d")
    if period == "week":
        iso = ts.isocalendar()
        return f"{iso[0]}-W{iso[1]:02d}"
    # month
    return ts.strftime("%Y-%m")


def build_timeline(commits: List[Commit], period: Period = "month") -> TimelineReport:
    """Group *commits* into time buckets determined by *period*."""
    buckets: Dict[str, TimelineBucket] = {}

    for commit in commits:
        try:
            ts = datetime.fromtimestamp(int(commit.date), tz=timezone.utc)
        except (ValueError, TypeError, AttributeError):
            continue
        label = _bucket_label(ts, period)
        if label not in buckets:
            buckets[label] = TimelineBucket(label=label)
        buckets[label].commits.append(commit)

    sorted_buckets = [buckets[k] for k in sorted(buckets)]
    return TimelineReport(period=period, buckets=sorted_buckets)


def format_timeline(report: TimelineReport) -> str:
    """Return a Markdown-formatted timeline report."""
    lines = [f"## Commit Timeline ({report.period})", ""]
    if not report.buckets:
        lines.append("_No commits found._")
        return "\n".join(lines)
    for bucket in report.buckets:
        lines.append(f"### {bucket.label}")
        for commit in bucket.commits:
            lines.append(f"- `{commit.hash[:7]}` {commit.message} *(by {commit.author})*")
        lines.append("")
    return "\n".join(lines)
