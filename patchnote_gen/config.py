"""Configuration loader for patchnote-gen."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional
import json

DEFAULT_CONFIG_PATH = Path(".patchnote.json")


@dataclass
class PatchnoteConfig:
    title: str = "Changelog"
    version: Optional[str] = None
    date: Optional[str] = None
    group_by_type: bool = True
    output_file: str = "CHANGELOG.md"
    template_file: Optional[str] = None
    type_labels: Dict[str, str] = field(default_factory=lambda: {
        "feat": "Features",
        "fix": "Bug Fixes",
        "docs": "Documentation",
        "chore": "Chores",
        "refactor": "Refactoring",
        "test": "Tests",
        "perf": "Performance",
    })
    exclude_types: list = field(default_factory=list)


def load_config(path: Path = DEFAULT_CONFIG_PATH) -> PatchnoteConfig:
    """Load configuration from a JSON file, falling back to defaults."""
    if not path.exists():
        return PatchnoteConfig()

    with path.open("r") as f:
        data = json.load(f)

    config = PatchnoteConfig()
    for key, value in data.items():
        if hasattr(config, key):
            setattr(config, key, value)

    return config


def save_config(config: PatchnoteConfig, path: Path = DEFAULT_CONFIG_PATH) -> None:
    """Persist a PatchnoteConfig to a JSON file."""
    data = {
        "title": config.title,
        "version": config.version,
        "date": config.date,
        "group_by_type": config.group_by_type,
        "output_file": config.output_file,
        "template_file": config.template_file,
        "type_labels": config.type_labels,
        "exclude_types": config.exclude_types,
    }
    with path.open("w") as f:
        json.dump(data, f, indent=2)


def config_to_template_config(config: PatchnoteConfig):
    """Convert PatchnoteConfig to TemplateConfig."""
    from patchnote_gen.template_engine import TemplateConfig
    return TemplateConfig(
        title=config.title,
        version=config.version,
        date=config.date,
        group_by_type=config.group_by_type,
        type_labels=config.type_labels,
    )
