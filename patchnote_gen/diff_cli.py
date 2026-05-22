"""CLI sub-command: patchnote-diff — show diff stats for a commit range."""

from __future__ import annotations

import argparse
import sys

from patchnote_gen.diff_stats import get_diff_stats, summarise_stats
from patchnote_gen.git_parser import get_commits


def build_diff_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # noqa: E501
    kwargs = dict(
        prog="patchnote-diff",
        description="Show diff statistics for a range of commits.",
    )
    if parent is not None:
        parser = parent.add_parser("diff", **kwargs)
    else:
        parser = argparse.ArgumentParser(**kwargs)

    parser.add_argument("--since", default=None, help="Start ref / tag")
    parser.add_argument("--until", default="HEAD", help="End ref / tag")
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print only the aggregated summary",
    )
    parser.add_argument(
        "--repo",
        default=".",
        metavar="PATH",
        help="Path to the git repository (default: .)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_diff_parser()
    args = parser.parse_args(argv)

    commits = get_commits(since=args.since, until=args.until, repo_path=args.repo)
    if not commits:
        print("No commits found in the specified range.", file=sys.stderr)
        return 1

    shas = [c.sha for c in commits if c.sha]
    stats = get_diff_stats(shas, repo_path=args.repo)

    if not stats:
        print("Could not retrieve diff statistics.", file=sys.stderr)
        return 1

    if not args.summary:
        for stat in stats:
            print(f"{stat.sha[:7]}  {stat}")
        print()

    summary = summarise_stats(stats)
    print(
        f"Total: {summary['total_commits']} commit(s), "
        f"{summary['total_files_changed']} file(s) changed, "
        f"+{summary['total_insertions']} -{summary['total_deletions']} "
        f"(net {summary['net_lines']:+d})"
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
