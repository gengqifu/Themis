from pathlib import Path

from themis.hooks import run_pre_commit_hook


def test_run_pre_commit_hook_allows_commit_when_exempted_by_path(
    tmp_path: Path, monkeypatch
) -> None:
    repo_root = tmp_path
    hooks_dir = repo_root / ".git" / "hooks"
    hooks_dir.mkdir(parents=True)
    (repo_root / ".themis.backend.yml").write_text(
        "allowlist:\n  paths:\n    - secrets/**\n",
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
            result.stdout = "diff --git a/secrets/a.txt b/secrets/a.txt\n@@ -0,0 +1 @@\n+x"
            result.stderr = ""
        else:
            result.returncode = 0
            result.stdout = '{"findings":[]}'
            result.stderr = ""
        return result

    monkeypatch.setattr("themis.hooks.run_command", fake_run)
    code = run_pre_commit_hook(repo_root=repo_root, platform="backend")
    assert code == 0


def test_run_pre_commit_hook_allows_commit_when_exempted_by_baseline(
    tmp_path: Path, monkeypatch
) -> None:
    repo_root = tmp_path
    hooks_dir = repo_root / ".git" / "hooks"
    hooks_dir.mkdir(parents=True)
    baseline_file = repo_root / ".themis-baseline.json"
    baseline_file.write_text("[]", encoding="utf-8")
    (repo_root / ".themis.backend.yml").write_text(
        "baseline: .themis-baseline.json\n",
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
            result.stdout = "diff --git a/a.txt b/a.txt\n@@ -0,0 +1 @@\n+x"
            result.stderr = ""
        else:
            result.returncode = 0
            result.stdout = '{"findings":[]}'
            result.stderr = ""
        return result

    monkeypatch.setattr("themis.hooks.run_command", fake_run)
    code = run_pre_commit_hook(repo_root=repo_root, platform="backend")
    assert code == 0
