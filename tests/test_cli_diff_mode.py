from pathlib import Path

from themis.cli import main


def test_cli_diff_mode_uses_diff_file(tmp_path: Path, monkeypatch) -> None:
    # file contains secret on line 2
    target = tmp_path / "a.txt"
    target.write_text("line1\nBEGIN RSA PRIVATE KEY\n", encoding="utf-8")
    diff = tmp_path / "d.patch"
    diff.write_text(
        """diff --git a/a.txt b/a.txt
--- a/a.txt
+++ b/a.txt
@@ -1,1 +1,2 @@
 line1
+BEGIN RSA PRIVATE KEY
""",
        encoding="utf-8",
    )
    # provide diff mode config
    cfg = tmp_path / ".themis.android.yml"
    cfg.write_text("scan:\n  mode: diff\n", encoding="utf-8")
    monkeypatch.setenv("CI_MERGE_REQUEST_DIFF_URL", "")
    exit_code = main(
        ["scan", str(tmp_path), "--platform", "android", "--diff-file", str(diff)]
    )
    assert exit_code == 2
