from __future__ import annotations

import json
from typing import Dict, Iterable, List, Optional


def redact(value: Optional[str], *, keep: int = 2) -> str:
    if not value:
        return ""
    if len(value) <= keep * 2:
        return "***"
    return f"{value[:keep]}***{value[-keep:]}"


def to_json(findings: Iterable[Dict], *, redact_keep: int = 2) -> str:
    items: List[Dict] = []
    for f in findings:
        items.append(
            {
                "rule_id": f.get("rule_id", ""),
                "severity": f.get("severity", ""),
                "file": f.get("file", ""),
                "line": f.get("line", 0),
                "message": f.get("message", ""),
                "preview": redact(f.get("match"), keep=redact_keep),
            }
        )
    return json.dumps({"findings": items}, ensure_ascii=False)


def to_text(findings: Iterable[Dict], *, redact_keep: int = 2) -> str:
    lines: List[str] = []
    for f in findings:
        preview = redact(f.get("match"), keep=redact_keep)
        lines.append(
            f"{f.get('severity','')} {f.get('rule_id','')} "
            f"{f.get('file','')}:{f.get('line',0)} "
            f"{f.get('message','')} {preview}".strip()
        )
    return "\n".join(lines)
