from themis.scanner import scan_text


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
