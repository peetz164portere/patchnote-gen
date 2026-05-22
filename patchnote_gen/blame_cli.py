"""CLI entry-point for the blame sub-command."""
from __future__ import annotations

import argparse
import sys

from .git_parser import get_commits
from .blame import collect_blame, format_blame


def build_blame_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    kwargs = dict(description="Show per-author file-touch blame report")
    if parent is not None:
        parser = parent.add_parser("blame", **kwargs)
    else:
        parser = argparse.ArgumentParser(prog="patchnote-blame", **kwargs)

    parser.add_argument("--since", default=None, metavar="REF", help="Start ref/tag")
    parser.add_argument("--until", default=None, metavar="REF", help="End ref/tag")
    parser.add_argument(
        "--top",
        type=int,
        default=None,
        metavar="N",
        help="Show only top N authors by commit count",
    )
    parser.add_argument(
        "--output", "-o", default=None, metavar="FILE", help="Write output to file"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_blame_parser()
    args = parser.parse_args(argv)

    commits = get_commits(since=args.since, until=args.until)
    if not commits:
        print("No commits found.", file=sys.stderr)
        return 1

    blame = collect_blame(commits)
    report = format_blame(blame, top_n=args.top)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(report + "\n")
    else:
        print(report)

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
