"""Commit trend analysis: velocity and activity patterns over time."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from .git_parser import Commit


@dataclass
class TrendWindow:
    label: str
    commit_count: int
    authors: List[str] = field(default_factory=list)
    types: Dict[str, int] = field(default_factory=dict)

    @property
    def unique_authors(self) -> int:
        return len(set(self.authors))

    def __str__(self) -> str:
        type_summary = ", ".join(
            f"{t}:{c}" for t, c in sorted(self.types.items(), key=lambda x: -x[1])
        )
        return (
            f"{self.label}: {self.commit_count} commits "
            f"({self.unique_authors} authors) [{type_summary}]"
        )


@dataclass
class TrendReport:
    windows: List[TrendWindow]
    granularity: str  # 'day' | 'week' | 'month'

    @property
    def peak_window(self) -> Optional[TrendWindow]:
        return max(self.windows, key=lambda w: w.commit_count) if self.windows else None

    @property
    def average_velocity(self) -> float:
        if not self.windows:
            return 0.0
        return sum(w.commit_count for w in self.windows) / len(self.windows)

    def __str__(self) -> str:
        lines = [f"Trend report ({self.granularity}):",
                 f"  Windows : {len(self.windows)}",
                 f"  Avg/window: {self.average_velocity:.1f}"]
        if self.peak_window:
            lines.append(f"  Peak    : {self.peak_window.label} ({self.peak_window.commit_count} commits)")
        return "\n".join(lines)


def _window_label(dt: datetime, granularity: str) -> str:
    if granularity == "day":
        return dt.strftime("%Y-%m-%d")
    if granularity == "week":
        monday = dt - timedelta(days=dt.weekday())
        return monday.strftime("W%Y-%m-%d")
    return dt.strftime("%Y-%m")


def build_trend(commits: List[Commit], granularity: str = "week") -> TrendReport:
    """Group commits into time windows and compute velocity metrics."""
    if granularity not in ("day", "week", "month"):
        raise ValueError(f"Unknown granularity: {granularity!r}")

    buckets: Dict[str, TrendWindow] = {}

    for commit in commits:
        label = _window_label(commit.date, granularity)
        if label not in buckets:
            buckets[label] = TrendWindow(label=label, commit_count=0)
        w = buckets[label]
        w.commit_count += 1
        w.authors.append(commit.author)
        if commit.commit_type:
            w.types[commit.commit_type] = w.types.get(commit.commit_type, 0) + 1

    windows = [buckets[k] for k in sorted(buckets)]
    return TrendReport(windows=windows, granularity=granularity)


def format_trend(report: TrendReport) -> str:
    lines = [str(report), ""]
    for w in report.windows:
        lines.append(f"  {w}")
    return "\n".join(lines)
