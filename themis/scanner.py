from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

from .file_utils import is_binary_file, is_too_large


def scan_text(
    text: str,
    *,
    rules: Sequence[Dict],
    file_path: str = "<memory>",
    only_lines: List[int] | None = None,
) -> List[Dict]:
    findings: List[Dict] = []
    lines = text.splitlines()
    for idx, line in enumerate(lines, start=1):
        if only_lines is not None and idx not in only_lines:
            continue
        for rule in rules:
            if not rule.get("enabled", True):
                continue
            if rule.get("type") != "regex":
                continue
            pattern = rule.get("pattern", "")
            if not pattern:
                continue
            if re.search(pattern, line):
                findings.append(
                    {
                        "rule_id": rule.get("id", ""),
                        "severity": rule.get("severity", ""),
                        "file": file_path,
                        "line": idx,
                        "message": rule.get("message", ""),
                        "match": line,
                    }
                )
    return findings


def scan_file(path: Path, *, rules: Sequence[Dict], max_file_size_bytes: int) -> List[Dict]:
    if is_too_large(path, max_file_size_bytes=max_file_size_bytes) or is_binary_file(path):
        return []
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []
    return scan_text(content, rules=rules, file_path=str(path))


def _iter_files(paths: Iterable[str]) -> Iterable[Path]:
    for p in paths:
        path = Path(p)
        if path.is_dir():
            for root, _, files in os.walk(path):
                for name in files:
                    yield Path(root) / name
        elif path.is_file():
            yield path


def scan_paths(
    paths: Iterable[str],
    *,
    rules: Sequence[Dict],
    max_file_size_bytes: int,
    only_lines: Dict[str, List[int]] | None = None,
) -> List[Dict]:
    findings: List[Dict] = []
    for path in _iter_files(paths):
        if only_lines is not None:
            rel = str(path)
            if rel not in only_lines:
                continue
            if is_too_large(path, max_file_size_bytes=max_file_size_bytes) or is_binary_file(path):
                continue
            findings.extend(
                scan_text(
                    path.read_text(encoding="utf-8", errors="ignore"),
                    rules=rules,
                    file_path=rel,
                    only_lines=only_lines[rel],
                )
            )
        else:
            findings.extend(scan_file(path, rules=rules, max_file_size_bytes=max_file_size_bytes))
    return findings
