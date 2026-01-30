import json

from themis.report import to_json, to_text


def test_report_redaction_default_keep_two() -> None:
    findings = [
        {
            "rule_id": "R1",
            "severity": "high",
            "file": "a.txt",
            "line": 3,
            "message": "msg",
            "match": "ABCDEF1234",
        }
    ]
    text = to_text(findings)
    assert "AB***34" in text

    data = json.loads(to_json(findings))
    assert data["findings"][0]["preview"] == "AB***34"


def test_report_min_fields_present() -> None:
    findings = [
        {
            "rule_id": "R2",
            "severity": "low",
            "file": "b.txt",
            "line": 1,
            "message": "m",
        }
    ]
    data = json.loads(to_json(findings))
    f = data["findings"][0]
    assert f["rule_id"] == "R2"
    assert f["severity"] == "low"
    assert f["file"] == "b.txt"
    assert f["line"] == 1
    assert f["message"] == "m"
