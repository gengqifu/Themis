from pathlib import Path

import pytest

from themis.hooks import run_pre_commit_hook


def test_run_pre_commit_hook_fails_outside_git_repo(tmp_path: Path, capsys) -> None:
    code = run_pre_commit_hook(repo_root=tmp_path, platform="backend")
    assert code != 0
    assert "not a git repository" in capsys.readouterr().err.lower()


def test_run_pre_commit_hook_fails_when_cached_diff_command_failed(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo_root = tmp_path
    hooks_dir = repo_root / ".git" / "hooks"
    hooks_dir.mkdir(parents=True)

    def fake_run(*args, **kwargs):
        class Result:
            returncode = 128
            stdout = ""
            stderr = "fatal: bad revision"

        return Result()

    monkeypatch.setattr("themis.hooks.run_command", fake_run)
    code = run_pre_commit_hook(repo_root=repo_root, platform="backend")
    assert code != 0
    assert "failed to read staged diff" in capsys.readouterr().err.lower()


def test_run_pre_commit_hook_fails_when_cached_diff_is_empty(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo_root = tmp_path
    hooks_dir = repo_root / ".git" / "hooks"
    hooks_dir.mkdir(parents=True)

    def fake_run(*args, **kwargs):
        class Result:
            returncode = 0
            stdout = ""
            stderr = ""

        return Result()

    monkeypatch.setattr("themis.hooks.run_command", fake_run)
    code = run_pre_commit_hook(repo_root=repo_root, platform="backend")
    assert code != 0
    assert "staged diff is empty" in capsys.readouterr().err.lower()


def test_run_pre_commit_hook_fails_when_scan_command_failed(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo_root = tmp_path
    hooks_dir = repo_root / ".git" / "hooks"
    hooks_dir.mkdir(parents=True)

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
            result.returncode = 1
            result.stdout = ""
            result.stderr = "critical finding"
        return result

    monkeypatch.setattr("themis.hooks.run_command", fake_run)
    code = run_pre_commit_hook(repo_root=repo_root, platform="backend")
    assert code != 0
    assert "scan failed" in capsys.readouterr().err.lower()
