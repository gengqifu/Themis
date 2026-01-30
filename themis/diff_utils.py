from __future__ import annotations

import re
from typing import Dict, List

HUNK_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


def parse_unified_diff(diff_text: str) -> Dict[str, List[int]]:
    file_lines: Dict[str, List[int]] = {}
    current_file: str | None = None
    new_line_no: int | None = None

    for line in diff_text.splitlines():
        if line.startswith("+++ "):
            path = line[4:].strip()
            if path.startswith("b/"):
                path = path[2:]
            current_file = path
            file_lines.setdefault(current_file, [])
            continue

        match = HUNK_RE.match(line)
        if match:
            new_line_no = int(match.group(1))
            continue

        if current_file is None or new_line_no is None:
            continue

        if line.startswith("+") and not line.startswith("+++"):
            file_lines[current_file].append(new_line_no)
            new_line_no += 1
        elif line.startswith("-") and not line.startswith("---"):
            continue
        else:
            new_line_no += 1

    return file_lines
