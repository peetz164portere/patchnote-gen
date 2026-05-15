"""Command-line interface for patchnote-gen."""

import argparse
import sys
from pathlib import Path

from patchnote_gen.config import load_config, save_config, config_to_template_config
from patchnote_gen.git_parser import get_commits
from patchnote_gen.template_engine import render_markdown, render_from_template_file


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="patchnote-gen",
        description="Generate formatted changelogs from git commit history.",
    )
    parser.add_argument(
        "--since",
        metavar="REF",
        default=None,
        help="Git ref (tag, commit, branch) to start from (e.g. v1.0.0).",
    )
    parser.add_argument(
        "--until",
        metavar="REF",
        default="HEAD",
        help="Git ref to end at (default: HEAD).",
    )
    parser.add_argument(
        "--output", "-o",
        metavar="FILE",
        default=None,
        help="Write output to FILE instead of stdout.",
    )
    parser.add_argument(
        "--template",
        metavar="FILE",
        default=None,
        help="Path to a Jinja2 template file to use for rendering.",
    )
    parser.add_argument(
        "--config",
        metavar="FILE",
        default="patchnote.toml",
        help="Path to config file (default: patchnote.toml).",
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="Write a default config file and exit.",
    )
    parser.add_argument(
        "--version",
        metavar="VER",
        default=None,
        help="Version string to use in the changelog header.",
    )
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    config = load_config(args.config)

    if args.init:
        save_config(config, args.config)
        print(f"Config written to {args.config}")
        return 0

    if args.version:
        config.version = args.version

    commits = get_commits(since=args.since, until=args.until)
    if not commits:
        print("No commits found.", file=sys.stderr)
        return 1

    tmpl_config = config_to_template_config(config)

    if args.template:
        output = render_from_template_file(Path(args.template), commits, tmpl_config)
    else:
        output = render_markdown(commits, tmpl_config)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Changelog written to {args.output}")
    else:
        print(output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
