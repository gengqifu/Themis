from pathlib import Path

from themis.diff_utils import build_lines_map_from_diff, parse_unified_diff, resolve_paths


def test_parse_unified_diff_collects_added_lines() -> None:
    diff = """diff --git a/a.txt b/a.txt
index 111..222 100644
--- a/a.txt
+++ b/a.txt
@@ -1,2 +1,3 @@
 line1
+added1
 line2
@@ -5,2 +6,3 @@
 line5
+added2
 line6
diff --git a/b.txt b/b.txt
index 333..444 100644
--- a/b.txt
+++ b/b.txt
@@ -10,1 +10,2 @@
 line10
+added3
"""
    result = parse_unified_diff(diff)
    assert result["a.txt"] == [2, 7]
    assert result["b.txt"] == [11]


def test_resolve_paths(tmp_path: Path) -> None:
    mapping = {"a.txt": [1, 2]}
    resolved = resolve_paths(mapping, repo_root=str(tmp_path))
    assert str(tmp_path / "a.txt") in resolved


def test_build_lines_map_from_diff(tmp_path: Path) -> None:
    diff = """diff --git a/a.txt b/a.txt
--- a/a.txt
+++ b/a.txt
@@ -1,1 +1,2 @@
 line1
+added
"""
    mapping = build_lines_map_from_diff(diff, repo_root=str(tmp_path))
    assert str(tmp_path / "a.txt") in mapping
    assert mapping[str(tmp_path / "a.txt")] == [2]


def test_parse_unified_diff_without_plus_header_uses_diff_git() -> None:
    diff = """diff --git a/a.txt b/a.txt
@@ -1,1 +1,2 @@
 line1
+added
"""
    result = parse_unified_diff(diff)
    assert result["a.txt"] == [2]
