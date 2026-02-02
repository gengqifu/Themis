from pathlib import Path

from themis.config import load_config
from themis.gitlab_mr import build_mr_scan_output


def test_build_mr_scan_output_uses_diff_lines_and_masks_value(tmp_path: Path) -> None:
    target = tmp_path / "a.txt"
    target.write_text("line1\nBEGIN RSA PRIVATE KEY\n", encoding="utf-8")

    cfg = load_config(platform=None, cwd=str(tmp_path))

    diff_text = """diff --git a/a.txt b/a.txt
--- a/a.txt
+++ b/a.txt
@@ -1,1 +1,2 @@
 line1
+BEGIN RSA PRIVATE KEY
"""
    body = build_mr_scan_output(
        paths=[str(tmp_path)],
        config=cfg,
        diff_text=diff_text,
        repo_root=str(tmp_path),
    )
    assert "PRIVATE_KEY_BLOCK" in body
    assert "BEGIN RSA PRIVATE KEY" not in body
