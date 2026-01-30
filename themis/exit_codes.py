from __future__ import annotations

from typing import Iterable, Dict

from .rules import SEVERITY_ORDER


def compute_exit_code(
    findings: Iterable[Dict],
    *,
    block_threshold: str = "critical",
    error: bool = False,
) -> int:
    if error:
        return 1
    threshold = SEVERITY_ORDER.get(block_threshold, 0)
    for f in findings:
        sev = SEVERITY_ORDER.get(str(f.get("severity", "")).lower(), 0)
        if sev >= threshold:
            return 2
    return 0
