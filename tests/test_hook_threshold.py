from themis.hooks import resolve_block_on_severity


def test_resolve_block_on_severity_uses_default_critical() -> None:
    result = resolve_block_on_severity(cli_value=None, config={})
    assert result == "critical"


def test_resolve_block_on_severity_uses_config_when_cli_missing() -> None:
    result = resolve_block_on_severity(
        cli_value=None,
        config={"scan": {"block_on_severity": "high"}},
    )
    assert result == "high"


def test_resolve_block_on_severity_cli_overrides_config() -> None:
    result = resolve_block_on_severity(
        cli_value="critical",
        config={"scan": {"block_on_severity": "low"}},
    )
    assert result == "critical"


def test_resolve_block_on_severity_rejects_invalid_value() -> None:
    try:
        resolve_block_on_severity(
            cli_value="invalid",
            config={"scan": {"block_on_severity": "critical"}},
        )
    except ValueError as exc:
        assert "invalid block_on_severity" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError for invalid severity")
