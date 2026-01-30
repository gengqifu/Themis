from __future__ import annotations

from pathlib import Path


def is_too_large(path: Path, *, max_file_size_bytes: int) -> bool:
    try:
        return path.stat().st_size > max_file_size_bytes
    except FileNotFoundError:
        return False


def is_binary_bytes(data: bytes) -> bool:
    if not data:
        return False
    # Heuristic: presence of NUL byte indicates binary
    return b"\x00" in data


def is_binary_file(path: Path, *, sample_size: int = 4096) -> bool:
    try:
        with path.open("rb") as f:
            sample = f.read(sample_size)
    except FileNotFoundError:
        return False
    return is_binary_bytes(sample)
