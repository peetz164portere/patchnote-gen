"""Tests for the config loader module."""

import json
import pytest
from pathlib import Path

from patchnote_gen.config import (
    PatchnoteConfig,
    load_config,
    save_config,
    config_to_template_config,
)


def test_load_config_defaults_when_no_file(tmp_path):
    config = load_config(tmp_path / "nonexistent.json")
    assert config.title == "Changelog"
    assert config.group_by_type is True
    assert config.output_file == "CHANGELOG.md"
    assert config.version is None


def test_load_config_from_file(tmp_path):
    cfg_file = tmp_path / ".patchnote.json"
    cfg_file.write_text(json.dumps({
        "title": "My Project",
        "version": "2.0.0",
        "group_by_type": False,
        "output_file": "CHANGES.md"
    }))
    config = load_config(cfg_file)
    assert config.title == "My Project"
    assert config.version == "2.0.0"
    assert config.group_by_type is False
    assert config.output_file == "CHANGES.md"


def test_load_config_partial_override(tmp_path):
    cfg_file = tmp_path / ".patchnote.json"
    cfg_file.write_text(json.dumps({"title": "Partial"}))
    config = load_config(cfg_file)
    assert config.title == "Partial"
    assert config.group_by_type is True  # default preserved


def test_load_config_ignores_unknown_keys(tmp_path):
    cfg_file = tmp_path / ".patchnote.json"
    cfg_file.write_text(json.dumps({"unknown_key": "value", "title": "Safe"}))
    config = load_config(cfg_file)
    assert config.title == "Safe"
    assert not hasattr(config, "unknown_key")


def test_save_and_reload_config(tmp_path):
    cfg_file = tmp_path / ".patchnote.json"
    original = PatchnoteConfig(
        title="Saved Config",
        version="3.1.0",
        date="2024-06-01",
        output_file="OUT.md"
    )
    save_config(original, cfg_file)
    loaded = load_config(cfg_file)
    assert loaded.title == "Saved Config"
    assert loaded.version == "3.1.0"
    assert loaded.date == "2024-06-01"
    assert loaded.output_file == "OUT.md"


def test_save_config_creates_valid_json(tmp_path):
    cfg_file = tmp_path / ".patchnote.json"
    save_config(PatchnoteConfig(), cfg_file)
    data = json.loads(cfg_file.read_text())
    assert "title" in data
    assert "type_labels" in data
    assert isinstance(data["type_labels"], dict)


def test_config_to_template_config():
    config = PatchnoteConfig(
        title="Template Test",
        version="1.0.0",
        date="2024-03-10",
        group_by_type=True,
    )
    tc = config_to_template_config(config)
    assert tc.title == "Template Test"
    assert tc.version == "1.0.0"
    assert tc.date == "2024-03-10"
    assert tc.group_by_type is True


def test_config_exclude_types_default():
    config = PatchnoteConfig()
    assert config.exclude_types == []
