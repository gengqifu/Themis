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
    threshold_key = str(block_threshold).lower().strip()
    threshold = SEVERITY_ORDER.get(threshold_key, 0)
    for f in findings:
        sev_key = str(f.get("severity", "")).lower().strip()
        sev = SEVERITY_ORDER.get(sev_key, 0)
        if sev >= threshold:
            return 2
    return 0
