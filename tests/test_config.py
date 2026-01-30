from pathlib import Path

import pytest

from themis.config import load_config
from themis.errors import ConfigError


def write_yaml(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def test_load_config_with_explicit_path(tmp_path: Path) -> None:
    cfg_path = tmp_path / "custom.yml"
    write_yaml(cfg_path, "scan:\n  mode: diff\n")
    cfg = load_config(config_path=str(cfg_path), platform="android", cwd=str(tmp_path))
    assert cfg["scan"]["mode"] == "diff"


def test_load_config_with_platform_default_file(tmp_path: Path) -> None:
    cfg_path = tmp_path / ".themis.android.yml"
    write_yaml(cfg_path, "scan:\n  mode: full\n")
    cfg = load_config(platform="android", cwd=str(tmp_path))
    assert cfg["scan"]["mode"] == "full"


def test_load_config_missing_uses_default_rules(tmp_path: Path) -> None:
    cfg = load_config(platform="android", cwd=str(tmp_path))
    assert "rules" in cfg
    assert isinstance(cfg["rules"], list)
    assert len(cfg["rules"]) > 0


def test_unknown_fields_raise(tmp_path: Path) -> None:
    cfg_path = tmp_path / "bad.yml"
    write_yaml(cfg_path, "unknown: 1\n")
    with pytest.raises(ConfigError):
        load_config(config_path=str(cfg_path), cwd=str(tmp_path))


def test_invalid_types_raise(tmp_path: Path) -> None:
    cfg_path = tmp_path / "bad_types.yml"
    write_yaml(cfg_path, "scan: 1\noutput: []\nrules: {}\n")
    with pytest.raises(ConfigError):
        load_config(config_path=str(cfg_path), cwd=str(tmp_path))
