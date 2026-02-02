from themis.gitlab_mr import format_scan_discussion_body


def test_format_scan_discussion_body_masks_secret_preview() -> None:
    findings = [
        {
            "severity": "critical",
            "rule_id": "GOOGLE_PLAY_KEYSTORE",
            "file": "app/build.gradle",
            "line": 12,
            "message": "Found sensitive value",
            "match": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        }
    ]
    body = format_scan_discussion_body(findings, redact_keep=2, limit=50)
    assert "AB***YZ" in body
    assert "ABCDEFGHIJKLMNOPQRSTUVWXYZ" not in body


def test_format_scan_discussion_body_contains_expected_fields() -> None:
    findings = [
        {
            "severity": "high",
            "rule_id": "GENERIC_TOKEN",
            "file": "src/main.js",
            "line": 8,
            "message": "Found token-like value",
            "match": "A1B2C3D4E5",
        }
    ]
    body = format_scan_discussion_body(findings, redact_keep=2, limit=50)
    assert "high" in body
    assert "GENERIC_TOKEN" in body
    assert "src/main.js:8" in body
    assert "Found token-like value" in body


def test_format_scan_discussion_body_limits_item_count() -> None:
    findings = [
        {
            "severity": "high",
            "rule_id": f"R{i}",
            "file": "src/a.py",
            "line": i,
            "message": "m",
            "match": "ABCD1234",
        }
        for i in range(1, 4)
    ]
    body = format_scan_discussion_body(findings, redact_keep=2, limit=2)
    assert "Total findings: 3" in body
    assert "Showing first 2 findings." in body
    assert "R1" in body
    assert "R2" in body
    assert "R3" not in body
