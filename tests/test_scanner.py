from themis.scanner import scan_text, scan_paths


def test_scan_text_matches_rule_and_line_number() -> None:
    text = "hello\nSECRET123\nworld"
    rules = [
        {
            "id": "SECRET_NUM",
            "severity": "high",
            "type": "regex",
            "pattern": r"SECRET\d+",
            "message": "发现测试密钥",
            "enabled": True,
        }
    ]
    findings = scan_text(text, rules=rules, file_path="test.txt")
    assert len(findings) == 1
    finding = findings[0]
    assert finding["rule_id"] == "SECRET_NUM"
    assert finding["file"] == "test.txt"
    assert finding["line"] == 2


def test_scan_text_only_lines() -> None:
    text = "a\nSECRET1\nSECRET2\nb"
    rules = [
        {
            "id": "SECRET",
            "severity": "high",
            "type": "regex",
            "pattern": r"SECRET\d+",
            "message": "found",
            "enabled": True,
        }
    ]
    findings = scan_text(text, rules=rules, file_path="x", only_lines=[2])
    assert len(findings) == 1
    assert findings[0]["line"] == 2


def test_scan_paths_full_mode_skips_binary_and_large(tmp_path) -> None:
    text_file = tmp_path / "ok.txt"
    text_file.write_text("BEGIN RSA PRIVATE KEY", encoding="utf-8")
    bin_file = tmp_path / "bin.dat"
    bin_file.write_bytes(b"\x00\x01\x02")
    big_file = tmp_path / "big.txt"
    big_file.write_text("A" * 50, encoding="utf-8")

    rules = [
        {
            "id": "PRIVATE_KEY_BLOCK",
            "severity": "critical",
            "type": "regex",
            "pattern": r"BEGIN (RSA|EC|OPENSSH|PGP) PRIVATE KEY",
            "message": "发现私钥块",
            "enabled": True,
        }
    ]
    findings = scan_paths(
        [str(tmp_path)], rules=rules, max_file_size_bytes=30, only_lines=None
    )
    assert len(findings) == 1
    assert findings[0]["file"].endswith("ok.txt")
