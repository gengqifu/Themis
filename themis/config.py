from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from .errors import ConfigError
from .rules import default_rules

ALLOWED_TOP_LEVEL_KEYS = {"scan", "rules", "allowlist", "baseline", "output"}


def _validate_schema(data: Dict[str, Any]) -> None:
    if "scan" in data and not isinstance(data["scan"], dict):
        raise ConfigError("scan 必须为对象")
    if "output" in data and not isinstance(data["output"], dict):
        raise ConfigError("output 必须为对象")
    if "allowlist" in data and not isinstance(data["allowlist"], dict):
        raise ConfigError("allowlist 必须为对象")
    if "baseline" in data and not isinstance(data["baseline"], str):
        raise ConfigError("baseline 必须为字符串路径")
    if "rules" in data and not isinstance(data["rules"], list):
        raise ConfigError("rules 必须为列表")


def _load_yaml(path: Path) -> Dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ConfigError(f"配置文件不存在: {path}") from exc
    data = yaml.safe_load(raw) if raw.strip() else {}
    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise ConfigError("配置文件顶层必须为对象")
    unknown = set(data.keys()) - ALLOWED_TOP_LEVEL_KEYS
    if unknown:
        raise ConfigError(f"未知配置字段: {', '.join(sorted(unknown))}")
    _validate_schema(data)
    return data


def load_config(
    *,
    config_path: Optional[str] = None,
    platform: Optional[str] = None,
    cwd: Optional[str] = None,
) -> Dict[str, Any]:
    base_dir = Path(cwd) if cwd else Path.cwd()

    if config_path:
        cfg = _load_yaml(Path(config_path))
    else:
        if not platform:
            cfg = {}
        else:
            cfg_file = base_dir / f".themis.{platform}.yml"
            cfg = _load_yaml(cfg_file) if cfg_file.exists() else {}

    if "rules" not in cfg:
        cfg["rules"] = default_rules()
    return cfg
