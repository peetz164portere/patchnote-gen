"""CLI sub-commands for managing git hooks.

Registered as the `patchnote-hook` entry point and also callable
via `patchnote-gen hook <subcommand>`.
"""

from __future__ import annotations

import argparse
import sys

from patchnote_gen.hook import install_hook, uninstall_hook, hook_status

VALID_HOOKS = ["post-commit", "commit-msg"]


def build_hook_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="patchnote-hook",
        description="Manage patchnote-gen git hooks.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # install
    p_install = sub.add_parser("install", help="Install a git hook")
    p_install.add_argument(
        "--type",
        dest="hook_type",
        choices=VALID_HOOKS,
        default="post-commit",
        help="Hook type to install (default: post-commit)",
    )
    p_install.add_argument("--repo", default=None, help="Path to repo root")

    # uninstall
    p_uninstall = sub.add_parser("uninstall", help="Uninstall a git hook")
    p_uninstall.add_argument(
        "--type",
        dest="hook_type",
        choices=VALID_HOOKS,
        default="post-commit",
    )
    p_uninstall.add_argument("--repo", default=None)

    # status
    p_status = sub.add_parser("status", help="Check if hook is installed")
    p_status.add_argument(
        "--type",
        dest="hook_type",
        choices=VALID_HOOKS,
        default="post-commit",
    )
    p_status.add_argument("--repo", default=None)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_hook_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "install":
            path = install_hook(args.hook_type, repo_root=args.repo)
            print(f"Installed {args.hook_type} hook at {path}")
            return 0

        elif args.command == "uninstall":
            removed = uninstall_hook(args.hook_type, repo_root=args.repo)
            if removed:
                print(f"Uninstalled {args.hook_type} hook.")
            else:
                print(f"Hook '{args.hook_type}' was not installed.")
            return 0

        elif args.command == "status":
            installed = hook_status(args.hook_type, repo_root=args.repo)
            state = "installed" if installed else "not installed"
            print(f"{args.hook_type}: {state}")
            return 0 if installed else 1

    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
