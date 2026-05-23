"""tag_summary_cli.py – CLI entry-point for tag-to-tag summaries."""
from __future__ import annotations

import argparse
import sys

from .tag_summary import build_tag_summary, format_tag_summary


def build_tag_summary_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="patchnote-tag-summary",
        description="Summarise commits between two git tags.",
    )
    p.add_argument("from_tag", help="Starting tag (exclusive)")
    p.add_argument(
        "to_tag",
        nargs="?",
        default="HEAD",
        help="Ending tag/ref (default: HEAD)",
    )
    p.add_argument(
        "--plain",
        action="store_true",
        help="Suppress markdown-style header",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_tag_summary_parser()
    args = parser.parse_args(argv)

    summary = build_tag_summary(args.from_tag, args.to_tag)

    if not summary.commits:
        print(f"No commits found between {args.from_tag} and {args.to_tag}.",
              file=sys.stderr)
        return 1

    text = format_tag_summary(summary)
    if args.plain:
        # Strip the markdown header line
        lines = text.splitlines()
        text = "\n".join(lines[1:]) if lines else text

    print(text)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
