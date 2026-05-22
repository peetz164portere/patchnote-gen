"""CLI entry-point for milestone detection."""

from __future__ import annotations

import argparse
import sys

from .git_parser import get_commits
from .milestone import detect_milestones, format_milestones


def build_milestone_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="patchnote-milestones",
        description="Detect and display release-highlight commits.",
    )
    parser.add_argument("--since", default=None, help="Start ref / tag")
    parser.add_argument("--until", default="HEAD", help="End ref (default: HEAD)")
    parser.add_argument(
        "--extra-types",
        nargs="*",
        default=[],
        metavar="TYPE",
        help="Additional commit types to treat as highlights",
    )
    parser.add_argument(
        "--title",
        default="Release Highlights",
        help="Section heading for the output",
    )
    parser.add_argument(
        "--plain",
        action="store_true",
        help="Print one milestone per line instead of Markdown",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_milestone_parser()
    args = parser.parse_args(argv)

    commits = get_commits(since=args.since, until=args.until)
    if not commits:
        print("No commits found.", file=sys.stderr)
        return 1

    milestones = detect_milestones(commits, extra_highlight_types=args.extra_types)
    if not milestones:
        print("No milestones detected.", file=sys.stderr)
        return 0

    if args.plain:
        for ms in milestones:
            print(str(ms))
    else:
        print(format_milestones(milestones, title=args.title), end="")

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
