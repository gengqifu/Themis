import json
from pathlib import Path

from themis.cli import main


def test_cli_scan_text_output(tmp_path: Path, capsys) -> None:
    f = tmp_path / "a.txt"
    f.write_text("BEGIN RSA PRIVATE KEY", encoding="utf-8")
    exit_code = main(["scan", str(tmp_path)])
    assert exit_code == 2
    captured = capsys.readouterr().out
    assert "PRIVATE_KEY_BLOCK" in captured


def test_cli_scan_json_output(tmp_path: Path, capsys) -> None:
    f = tmp_path / "a.txt"
    f.write_text("BEGIN RSA PRIVATE KEY", encoding="utf-8")
    exit_code = main(["scan", str(tmp_path), "--format", "json"])
    assert exit_code == 2
    data = json.loads(capsys.readouterr().out)
    assert "findings" in data
