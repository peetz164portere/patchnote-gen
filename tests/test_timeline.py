"""Tests for patchnote_gen.timeline."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from patchnote_gen.timeline import (
    TimelineBucket,
    TimelineReport,
    _bucket_label,
    build_timeline,
    format_timeline,
)


def _commit(date_ts: int, message: str = "feat: thing", author: str = "dev") -> MagicMock:
    c = MagicMock()
    c.date = str(date_ts)
    c.message = message
    c.author = author
    c.hash = "abcdef1234567"
    return c


# Unix timestamps for known dates
_JAN_05 = int(datetime(2024, 1, 5, tzinfo=timezone.utc).timestamp())
_JAN_20 = int(datetime(2024, 1, 20, tzinfo=timezone.utc).timestamp())
_FEB_10 = int(datetime(2024, 2, 10, tzinfo=timezone.utc).timestamp())


@pytest.fixture
def sample_commits():
    return [
        _commit(_JAN_05, "feat: alpha"),
        _commit(_JAN_20, "fix: beta"),
        _commit(_FEB_10, "chore: gamma"),
    ]


def test_bucket_label_day():
    ts = datetime(2024, 3, 15, tzinfo=timezone.utc)
    assert _bucket_label(ts, "day") == "2024-03-15"


def test_bucket_label_week():
    ts = datetime(2024, 1, 8, tzinfo=timezone.utc)  # ISO week 2
    label = _bucket_label(ts, "week")
    assert label == "2024-W02"


def test_bucket_label_month():
    ts = datetime(2024, 6, 1, tzinfo=timezone.utc)
    assert _bucket_label(ts, "month") == "2024-06"


def test_build_timeline_month_groups(sample_commits):
    report = build_timeline(sample_commits, period="month")
    assert report.period == "month"
    assert len(report.buckets) == 2
    labels = [b.label for b in report.buckets]
    assert "2024-01" in labels
    assert "2024-02" in labels


def test_build_timeline_bucket_counts(sample_commits):
    report = build_timeline(sample_commits, period="month")
    jan_bucket = next(b for b in report.buckets if b.label == "2024-01")
    assert jan_bucket.count == 2


def test_build_timeline_total(sample_commits):
    report = build_timeline(sample_commits, period="month")
    assert report.total == 3


def test_build_timeline_day(sample_commits):
    report = build_timeline(sample_commits, period="day")
    assert len(report.buckets) == 3


def test_build_timeline_skips_bad_date():
    bad = MagicMock()
    bad.date = "not-a-timestamp"
    bad.message = "fix: oops"
    bad.author = "ghost"
    bad.hash = "000000"
    report = build_timeline([bad], period="month")
    assert report.total == 0


def test_format_timeline_markdown(sample_commits):
    report = build_timeline(sample_commits, period="month")
    md = format_timeline(report)
    assert "## Commit Timeline" in md
    assert "2024-01" in md
    assert "abcdef1" in md


def test_format_timeline_empty():
    report = TimelineReport(period="week", buckets=[])
    md = format_timeline(report)
    assert "_No commits found._" in md


def test_timeline_report_summary(sample_commits):
    report = build_timeline(sample_commits, period="month")
    summary = report.summary()
    assert "Timeline (month)" in summary
    assert "2024-01: 2" in summary
