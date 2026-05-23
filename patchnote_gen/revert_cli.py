"""CLI entry-point for the revert detector."""

from __future__ import annotations

import argparse
import sys

from .git_parser import get_commits
from .revert import build_revert_report, format_revert_report


def build_revert_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="patchnote-reverts",
        description="List revert commits in a git range.",
    )
    p.add_argument("--since", default="", help="Start ref / tag (inclusive)")
    p.add_argument("--until", default="HEAD", help="End ref / tag (default: HEAD)")
    p.add_argument(
        "--repo",
        default=".",
        metavar="PATH",
        help="Path to git repository (default: current directory)",
    )
    p.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON instead of plain text",
    )
    return p


def main(argv: list[str] | None = None) -> int:  # pragma: no cover
    parser = build_revert_parser()
    args = parser.parse_args(argv)

    commits = get_commits(repo_path=args.repo, since=args.since, until=args.until)
    if not commits:
        print("No commits found.", file=sys.stderr)
        return 1

    report = build_revert_report(commits, since=args.since, until=args.until)

    if args.json:
        import json

        data = [
            {
                "hash": e.reverting.hash,
                "message": e.reverting.message,
                "target_sha": e.target_sha,
            }
            for e in report.reverts
        ]
        print(json.dumps(data, indent=2))
    else:
        print(format_revert_report(report))

    return 0
