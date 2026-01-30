from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class DiffSource:
    kind: str  # "url" or "file"
    value: str


def choose_diff_source(
    *, ci_merge_request_diff_url: Optional[str], diff_file: Optional[str]
) -> DiffSource:
    if ci_merge_request_diff_url:
        return DiffSource(kind="url", value=ci_merge_request_diff_url)
    if diff_file:
        return DiffSource(kind="file", value=diff_file)
    raise ValueError("No diff source provided")
