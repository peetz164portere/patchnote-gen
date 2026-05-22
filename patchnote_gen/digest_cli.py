"""CLI entry-point for the digest sub-command."""

from __future__ import annotations

import argparse
import sys
from datetime import date

from .git_parser import get_commits
from .digest import build_digest, format_digest


def build_digest_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    kwargs = dict(description="Generate a periodic activity digest from git history.")
    if parent is not None:
        parser = parent.add_parser("digest", **kwargs)
    else:
        parser = argparse.ArgumentParser(**kwargs)

    today = date.today().isoformat()
    parser.add_argument("--since", default="1 week ago", help="Start of the period (default: '1 week ago')")
    parser.add_argument("--until", default=today, help="End of the period (default: today)")
    parser.add_argument("--repo", default=".", help="Path to the git repository (default: current dir)")
    parser.add_argument("--output", "-o", default=None, help="Write digest to this file instead of stdout")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_digest_parser()
    args = parser.parse_args(argv)

    commits = get_commits(repo_path=args.repo, since=args.since, until=args.until)
    if not commits:
        print("No commits found for the specified range.", file=sys.stderr)
        return 1

    report = build_digest(commits, since=args.since, until=args.until)
    output = format_digest(report)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(output)
        print(f"Digest written to {args.output}")
    else:
        print(output)

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
