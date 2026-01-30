from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict, Iterable, List


def _normalize_match(match: str) -> str:
    return "".join(match.split())


def match_hash(match: str) -> str:
    normalized = _normalize_match(match)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def build_fingerprint(finding: Dict) -> Dict:
    return {
        "rule_id": finding.get("rule_id", ""),
        "file": finding.get("file", ""),
        "line": finding.get("line", 0),
        "hash": match_hash(finding.get("match", "")),
    }


def load_baseline(path: Path) -> List[Dict]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("items", [])


def write_baseline(path: Path, items: Iterable[Dict]) -> None:
    payload = {"items": list(items)}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def filter_findings(findings: Iterable[Dict], baseline_items: Iterable[Dict]) -> List[Dict]:
    baseline_set = {
        (i.get("rule_id"), i.get("file"), i.get("line"), i.get("hash"))
        for i in baseline_items
    }
    result: List[Dict] = []
    for f in findings:
        fp = build_fingerprint(f)
        key = (fp["rule_id"], fp["file"], fp["line"], fp["hash"])
        if key in baseline_set:
            continue
        result.append(f)
    return result
