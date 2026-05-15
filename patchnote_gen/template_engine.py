"""Template engine for rendering changelogs from commit data."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from pathlib import Path
import re

from patchnote_gen.git_parser import Commit


@dataclass
class TemplateConfig:
    title: str = "Changelog"
    version: Optional[str] = None
    date: Optional[str] = None
    group_by_type: bool = True
    type_labels: Dict[str, str] = field(default_factory=lambda: {
        "feat": "Features",
        "fix": "Bug Fixes",
        "docs": "Documentation",
        "chore": "Chores",
        "refactor": "Refactoring",
        "test": "Tests",
        "perf": "Performance",
    })


def group_commits(commits: List[Commit], config: TemplateConfig) -> Dict[str, List[Commit]]:
    """Group commits by their type using config labels."""
    groups: Dict[str, List[Commit]] = {}
    for commit in commits:
        label = config.type_labels.get(commit.type, commit.type or "Other")
        groups.setdefault(label, []).append(commit)
    return groups


def render_markdown(commits: List[Commit], config: TemplateConfig) -> str:
    """Render commits as a markdown changelog."""
    lines = []

    header = f"# {config.title}"
    if config.version:
        header += f" — {config.version}"
    if config.date:
        header += f" ({config.date})"
    lines.append(header)
    lines.append("")

    if config.group_by_type:
        groups = group_commits(commits, config)
        for label, group_commits_list in groups.items():
            lines.append(f"## {label}")
            lines.append("")
            for commit in group_commits_list:
                scope_part = f"**{commit.scope}**: " if commit.scope else ""
                lines.append(f"- {scope_part}{commit.message} (`{commit.hash[:7]}`)")            
            lines.append("")
    else:
        lines.append("## Changes")
        lines.append("")
        for commit in commits:
            lines.append(f"- {commit.message} (`{commit.hash[:7]}`)")
        lines.append("")

    return "\n".join(lines)


def render_from_template_file(commits: List[Commit], template_path: Path, config: TemplateConfig) -> str:
    """Render changelog using a custom template file with simple variable substitution."""
    template = template_path.read_text()
    grouped = group_commits(commits, config)

    sections = []
    for label, group_list in grouped.items():
        items = "\n".join(
            f"- {('**' + c.scope + '**: ') if c.scope else ''}{c.message} (`{c.hash[:7]}`)"
            for c in group_list
        )
        sections.append(f"### {label}\n{items}")

    rendered = template
    rendered = rendered.replace("{{title}}", config.title)
    rendered = rendered.replace("{{version}}", config.version or "")
    rendered = rendered.replace("{{date}}", config.date or "")
    rendered = rendered.replace("{{sections}}", "\n\n".join(sections))
    return rendered
