"""Utilities for writing changelog output to files or stdout."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path
from typing import Optional


PREPEND_SEPARATOR = "\n\n---\n\n"


def write_output(content: str, path: Optional[Path] = None) -> None:
    """Write *content* to *path* or stdout if path is None."""
    if path is None:
        sys.stdout.write(content)
        if not content.endswith("\n"):
            sys.stdout.write("\n")
    else:
        path.write_text(content, encoding="utf-8")


def prepend_to_file(content: str, path: Path) -> None:
    """Prepend *content* to an existing file, or create it if missing."""
    if path.exists():
        existing = path.read_text(encoding="utf-8")
        path.write_text(content + PREPEND_SEPARATOR + existing, encoding="utf-8")
    else:
        path.write_text(content, encoding="utf-8")


def append_to_file(content: str, path: Path) -> None:
    """Append *content* to an existing file, or create it if missing."""
    with path.open("a", encoding="utf-8") as fh:
        if path.stat().st_size > 0:
            fh.write(PREPEND_SEPARATOR)
        fh.write(content)


def stamp_filename(base: str, version: Optional[str] = None) -> str:
    """Return a filename stamped with version or today's date.

    Examples
    --------
    >>> stamp_filename("CHANGELOG", "1.2.3")
    'CHANGELOG-1.2.3.md'
    >>> stamp_filename("CHANGELOG")  # doctest: +SKIP
    'CHANGELOG-2024-01-15.md'
    """
    suffix = version if version else date.today().isoformat()
    return f"{base}-{suffix}.md"
