from __future__ import annotations

import hashlib
from pathlib import Path

from themis.hooks import run_pre_commit_hook


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_run_pre_commit_hook_keeps_workspace_files_unchanged(
    tmp_path: Path, monkeypatch
) -> None:
    repo_root = tmp_path
    (repo_root / ".git" / "hooks").mkdir(parents=True)
    (repo_root / ".themis.backend.yml").write_text("scan:\n  mode: diff\n", encoding="utf-8")
    tracked = repo_root / "a.txt"
    tracked.write_text("hello\n", encoding="utf-8")

    before = {
        str(repo_root / ".themis.backend.yml"): _sha256(repo_root / ".themis.backend.yml"),
        str(tracked): _sha256(tracked),
    }

    calls = {"n": 0}

    def fake_run(*args, **kwargs):
        calls["n"] += 1

        class Result:
            pass

        result = Result()
        if calls["n"] == 1:
            result.returncode = 0
            result.stdout = "diff --git a/a.txt b/a.txt\n@@ -0,0 +1 @@\n+hello\n"
            result.stderr = ""
        else:
            result.returncode = 0
            result.stdout = '{"findings":[]}'
            result.stderr = ""
        return result

    monkeypatch.setattr("themis.hooks.run_command", fake_run)
    code = run_pre_commit_hook(repo_root=repo_root, platform="backend")
    assert code == 0

    after = {
        str(repo_root / ".themis.backend.yml"): _sha256(repo_root / ".themis.backend.yml"),
        str(tracked): _sha256(tracked),
    }
    assert after == before
