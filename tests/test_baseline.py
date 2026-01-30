from pathlib import Path

from themis.baseline import (
    build_fingerprint,
    filter_findings,
    load_baseline,
    resolve_baseline_path,
    write_baseline,
)


def test_baseline_filtering() -> None:
    finding = {
        "rule_id": "R1",
        "file": "a.txt",
        "line": 2,
        "match": "secret 123",
    }
    fp = build_fingerprint(finding)
    filtered = filter_findings([finding], [fp])
    assert filtered == []


def test_baseline_write_and_load(tmp_path: Path) -> None:
    path = tmp_path / "baseline.json"
    items = [{"rule_id": "R1", "file": "a.txt", "line": 2, "hash": "h"}]
    write_baseline(path, items)
    loaded = load_baseline(path)
    assert loaded == items


def test_resolve_baseline_path(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    rel = "baseline.json"
    resolved = resolve_baseline_path(rel, repo_root=str(repo_root))
    assert resolved == repo_root / rel
