from themis.rules import default_rules


def test_default_rules_present() -> None:
    rules = default_rules()
    assert isinstance(rules, list)
    assert any(r.get("id") == "PRIVATE_KEY_BLOCK" for r in rules)
