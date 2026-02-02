from pathlib import Path

from themis.hooks import resolve_block_on_severity, run_pre_commit_hook


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


def test_run_pre_commit_hook_applies_configured_threshold(
    tmp_path: Path, monkeypatch
) -> None:
    repo_root = tmp_path
    (repo_root / ".git" / "hooks").mkdir(parents=True)
    (repo_root / ".themis.backend.yml").write_text(
        "scan:\n  block_on_severity: high\n",
        encoding="utf-8",
    )

    calls = {"n": 0}

    def fake_run(*args, **kwargs):
        calls["n"] += 1

        class Result:
            pass

        result = Result()
        if calls["n"] == 1:
            result.returncode = 0
            result.stdout = "diff --git a/a b/a\n@@ -0,0 +1 @@\n+x"
            result.stderr = ""
        else:
            result.returncode = 0
            result.stdout = (
                '{"findings":[{"severity":"high","rule_id":"R","file":"a","line":1,"message":"m"}]}'
            )
            result.stderr = ""
        return result

    monkeypatch.setattr("themis.hooks.run_command", fake_run)
    code = run_pre_commit_hook(repo_root=repo_root, platform="backend")
    assert code == 2


def test_run_pre_commit_hook_cli_threshold_overrides_config(
    tmp_path: Path, monkeypatch
) -> None:
    repo_root = tmp_path
    (repo_root / ".git" / "hooks").mkdir(parents=True)
    (repo_root / ".themis.backend.yml").write_text(
        "scan:\n  block_on_severity: low\n",
        encoding="utf-8",
    )

    calls = {"n": 0}

    def fake_run(*args, **kwargs):
        calls["n"] += 1

        class Result:
            pass

        result = Result()
        if calls["n"] == 1:
            result.returncode = 0
            result.stdout = "diff --git a/a b/a\n@@ -0,0 +1 @@\n+x"
            result.stderr = ""
        else:
            result.returncode = 0
            result.stdout = (
                '{"findings":[{"severity":"high","rule_id":"R","file":"a","line":1,"message":"m"}]}'
            )
            result.stderr = ""
        return result

    monkeypatch.setattr("themis.hooks.run_command", fake_run)
    code = run_pre_commit_hook(
        repo_root=repo_root,
        platform="backend",
        block_on_severity="critical",
    )
    assert code == 0
