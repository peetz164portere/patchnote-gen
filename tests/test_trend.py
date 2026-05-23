"""Tests for patchnote_gen.trend module."""

from datetime import datetime

import pytest

from patchnote_gen.git_parser import Commit
from patchnote_gen.trend import (
    TrendWindow,
    TrendReport,
    build_trend,
    format_trend,
    _window_label,
)


def _commit(author: str, date: datetime, msg: str = "feat: something") -> Commit:
    return Commit(hash="abc", author=author, date=date, raw_message=msg)


@pytest.fixture
def sample_commits():
    return [
        _commit("alice", datetime(2024, 3, 4), "feat: add login"),
        _commit("bob",   datetime(2024, 3, 5), "fix: crash"),
        _commit("alice", datetime(2024, 3, 11), "chore: cleanup"),
        _commit("carol", datetime(2024, 3, 11), "feat: dashboard"),
        _commit("bob",   datetime(2024, 4, 1), "fix: typo"),
    ]


def test_window_label_day():
    assert _window_label(datetime(2024, 3, 5), "day") == "2024-03-05"


def test_window_label_week():
    # 2024-03-05 is a Tuesday; Monday is 2024-03-04
    assert _window_label(datetime(2024, 3, 5), "week") == "W2024-03-04"


def test_window_label_month():
    assert _window_label(datetime(2024, 3, 5), "month") == "2024-03"


def test_build_trend_week_buckets(sample_commits):
    report = build_trend(sample_commits, granularity="week")
    assert report.granularity == "week"
    # week of 2024-03-04, week of 2024-03-11, week of 2024-04-01
    assert len(report.windows) == 3


def test_build_trend_month_buckets(sample_commits):
    report = build_trend(sample_commits, granularity="month")
    labels = [w.label for w in report.windows]
    assert "2024-03" in labels
    assert "2024-04" in labels
    assert len(report.windows) == 2


def test_build_trend_commit_counts(sample_commits):
    report = build_trend(sample_commits, granularity="month")
    march = next(w for w in report.windows if w.label == "2024-03")
    assert march.commit_count == 4


def test_build_trend_unique_authors(sample_commits):
    report = build_trend(sample_commits, granularity="month")
    march = next(w for w in report.windows if w.label == "2024-03")
    assert march.unique_authors == 2  # alice and bob in march first week


def test_build_trend_type_tally(sample_commits):
    report = build_trend(sample_commits, granularity="month")
    march = next(w for w in report.windows if w.label == "2024-03")
    assert march.types.get("feat", 0) == 2
    assert march.types.get("fix", 0) == 1


def test_peak_window(sample_commits):
    report = build_trend(sample_commits, granularity="month")
    assert report.peak_window is not None
    assert report.peak_window.label == "2024-03"


def test_average_velocity(sample_commits):
    report = build_trend(sample_commits, granularity="month")
    # 4 commits in march, 1 in april => avg = 2.5
    assert report.average_velocity == pytest.approx(2.5)


def test_invalid_granularity(sample_commits):
    with pytest.raises(ValueError, match="Unknown granularity"):
        build_trend(sample_commits, granularity="decade")


def test_format_trend_contains_header(sample_commits):
    report = build_trend(sample_commits, granularity="week")
    output = format_trend(report)
    assert "Trend report (week)" in output
    assert "Peak" in output


def test_trend_window_str():
    w = TrendWindow(label="2024-03", commit_count=3, authors=["alice", "bob"], types={"feat": 2, "fix": 1})
    s = str(w)
    assert "2024-03" in s
    assert "3 commits" in s
    assert "2 authors" in s
