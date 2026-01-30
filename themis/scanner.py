from __future__ import annotations

import re
from typing import Dict, List, Sequence


def scan_text(text: str, *, rules: Sequence[Dict], file_path: str = "<memory>") -> List[Dict]:
    findings: List[Dict] = []
    lines = text.splitlines()
    for idx, line in enumerate(lines, start=1):
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
