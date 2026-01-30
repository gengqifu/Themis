from typing import Any, Dict, List

SEVERITY_ORDER = {"low": 0, "medium": 1, "high": 2, "critical": 3}


def default_rules() -> List[Dict[str, Any]]:
    return [
        {
            "id": "PRIVATE_KEY_BLOCK",
            "severity": "critical",
            "type": "regex",
            "pattern": r"BEGIN (RSA|EC|OPENSSH|PGP) PRIVATE KEY",
            "message": "发现私钥块",
            "enabled": True,
        }
    ]
