"""patchnote-gen: Generates formatted changelogs from git commit history."""

__version__ = "0.1.0"
__author__ = "patchnote-gen contributors"

from patchnote_gen.git_parser import Commit, get_commits

__all__ = ["Commit", "get_commits"]
