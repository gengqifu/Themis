from themis.diff_utils import parse_unified_diff


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
