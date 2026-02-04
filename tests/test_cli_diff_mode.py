from pathlib import Path

from themis.cli import main


def test_cli_diff_mode_uses_diff_file(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
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


def test_cli_diff_mode_respects_block_on_severity(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    target = tmp_path / "b.txt"
    target.write_text("line1\nSECRET123\n", encoding="utf-8")
    diff = tmp_path / "b.patch"
    diff.write_text(
        """diff --git a/b.txt b/b.txt
--- a/b.txt
+++ b/b.txt
@@ -1,1 +1,2 @@
 line1
+SECRET123
""",
        encoding="utf-8",
    )
    cfg = tmp_path / ".themis.android.yml"
    cfg.write_text(
        "scan:\n"
        "  mode: diff\n"
        "  block_on_severity: high\n"
        "rules:\n"
        "  - id: TEST_HIGH\n"
        "    severity: high\n"
        "    type: regex\n"
        "    pattern: \"SECRET123\"\n"
        "    message: \"test high\"\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("CI_MERGE_REQUEST_DIFF_URL", "")
    exit_code = main(
        ["scan", str(tmp_path), "--platform", "android", "--diff-file", str(diff)]
    )
    assert exit_code == 2


def test_cli_diff_mode_invalid_block_on_severity_falls_back(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)
    target = tmp_path / "c.txt"
    target.write_text("line1\nSECRET123\n", encoding="utf-8")
    diff = tmp_path / "c.patch"
    diff.write_text(
        """diff --git a/c.txt b/c.txt
--- a/c.txt
+++ b/c.txt
@@ -1,1 +1,2 @@
 line1
+SECRET123
""",
        encoding="utf-8",
    )
    cfg = tmp_path / ".themis.android.yml"
    cfg.write_text(
        "scan:\n"
        "  mode: diff\n"
        "  block_on_severity: invalid\n"
        "rules:\n"
        "  - id: TEST_HIGH\n"
        "    severity: high\n"
        "    type: regex\n"
        "    pattern: \"SECRET123\"\n"
        "    message: \"test high\"\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("CI_MERGE_REQUEST_DIFF_URL", "")
    exit_code = main(
        ["scan", str(tmp_path), "--platform", "android", "--diff-file", str(diff)]
    )
    assert exit_code == 0
