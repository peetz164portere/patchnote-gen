"""CLI entry-point for the timeline subcommand."""

from __future__ import annotations

import argparse
import sys

from .git_parser import get_commits
from .timeline import build_timeline, format_timeline


def build_timeline_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    kwargs = dict(
        description="Show commit activity grouped by time period.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    if parent is not None:
        parser = parent.add_parser("timeline", **kwargs)
    else:
        parser = argparse.ArgumentParser(**kwargs)

    parser.add_argument("--since", default=None, metavar="REF", help="Start ref or date")
    parser.add_argument("--until", default=None, metavar="REF", help="End ref or date")
    parser.add_argument(
        "--period",
        choices=["day", "week", "month"],
        default="month",
        help="Bucket size for grouping commits",
    )
    parser.add_argument(
        "--markdown",
        action="store_true",
        default=False,
        help="Render as Markdown instead of plain summary",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_timeline_parser()
    args = parser.parse_args(argv)

    commits = get_commits(since=args.since, until=args.until)
    if not commits:
        print("No commits found.", file=sys.stderr)
        return 1

    report = build_timeline(commits, period=args.period)

    if args.markdown:
        print(format_timeline(report))
    else:
        print(report.summary())

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
