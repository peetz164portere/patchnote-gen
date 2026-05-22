"""CLI entry point for the compare sub-command."""

import argparse
import sys

from .compare import compare_refs, format_compare_result


def build_compare_parser(parent: argparse.ArgumentParser = None) -> argparse.ArgumentParser:
    if parent is None:
        parser = argparse.ArgumentParser(
            prog="patchnote-compare",
            description="Compare two git refs and summarise changes.",
        )
    else:
        parser = parent

    parser.add_argument(
        "from_ref",
        help="Starting ref (tag, branch, or commit SHA).",
    )
    parser.add_argument(
        "to_ref",
        nargs="?",
        default="HEAD",
        help="Ending ref (default: HEAD).",
    )
    parser.add_argument(
        "--repo",
        default=".",
        metavar="PATH",
        help="Path to the git repository (default: current directory).",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="List individual commits in addition to the summary.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON.",
    )
    return parser


def main(argv=None) -> int:
    parser = build_compare_parser()
    args = parser.parse_args(argv)

    result = compare_refs(
        from_ref=args.from_ref,
        to_ref=args.to_ref,
        repo_path=args.repo,
    )

    if result.total == 0:
        print(f"No commits found between {args.from_ref} and {args.to_ref}.", file=sys.stderr)
        return 1

    if args.json:
        import json
        payload = {
            "from_ref": result.from_ref,
            "to_ref": result.to_ref,
            "total": result.total,
            "breaking": len(result.breaking),
            "features": len(result.features),
            "fixes": len(result.fixes),
            "other": len(result.other),
            "summary": result.summary,
        }
        print(json.dumps(payload, indent=2))
    else:
        print(format_compare_result(result, verbose=args.verbose))

    return 0


if __name__ == "__main__":
    sys.exit(main())
