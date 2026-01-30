from __future__ import annotations

import re
from typing import Optional


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
