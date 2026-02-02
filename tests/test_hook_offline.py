from __future__ import annotations

import socket
from pathlib import Path

from themis.hooks import run_pre_commit_hook


def test_run_pre_commit_hook_runs_without_network(
    tmp_path: Path, monkeypatch
) -> None:
    repo_root = tmp_path
    (repo_root / ".git" / "hooks").mkdir(parents=True)
    (repo_root / ".themis.backend.yml").write_text("scan:\n  mode: diff\n", encoding="utf-8")

    class GuardedSocket(socket.socket):
        def connect(self, *args, **kwargs):  # type: ignore[override]
            raise AssertionError("network access is not allowed in hook")

    monkeypatch.setattr(socket, "socket", GuardedSocket)

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
