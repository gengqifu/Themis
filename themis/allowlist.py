from __future__ import annotations

import fnmatch
import re
from typing import Iterable, Optional


def is_ignored_by_comment(
    line: str,
    prev_line: Optional[str],
    *,
    rule_id: str,
    marker: str = "themis:ignore",
) -> bool:
    def _match(target: str) -> bool:
        if marker not in target:
            return False
        # exact rule-id ignore: "themis:ignore RULE_ID"
        m = re.search(rf"{re.escape(marker)}\s+(\S+)", target)
        if m:
            return m.group(1) == rule_id
        return True

    if _match(line):
        return True
    if prev_line and _match(prev_line):
        return True
    return False


def is_ignored_by_path(path: str, patterns: Iterable[str]) -> bool:
    for pat in patterns:
        if fnmatch.fnmatch(path, pat):
            return True
    return False
