"""CLI entry-point for the stats sub-command."""
from __future__ import annotations

import argparse
import sys

from .git_parser import get_commits
from .stats import compute_stats


def build_stats_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    kwargs = dict(
        prog="patchnote-stats",
        description="Print commit statistics for a revision range.",
    )
    if parent is not None:
        parser = parent.add_parser("stats", **kwargs)
    else:
        parser = argparse.ArgumentParser(**kwargs)

    parser.add_argument("--since", default=None, help="Start ref / tag")
    parser.add_argument("--until", default="HEAD", help="End ref (default: HEAD)")
    parser.add_argument("--repo", default=".", help="Path to git repository")
    parser.add_argument(
        "--json", dest="as_json", action="store_true", help="Output raw JSON"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_stats_parser()
    args = parser.parse_args(argv)

    commits = get_commits(repo_path=args.repo, since=args.since, until=args.until)
    if not commits:
        print("No commits found.", file=sys.stderr)
        return 1

    stats = compute_stats(commits)

    if args.as_json:
        import json

        print(
            json.dumps(
                {
                    "total": stats.total,
                    "breaking": stats.breaking,
                    "by_type": stats.by_type,
                    "by_scope": stats.by_scope,
                    "authors": stats.authors,
                },
                indent=2,
            )
        )
    else:
        print(stats.summary())

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
