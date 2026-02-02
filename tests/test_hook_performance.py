from __future__ import annotations

import json
import statistics
import time
from pathlib import Path

from themis.hooks import run_pre_commit_hook


def test_hook_performance_baseline_p95_p99(tmp_path: Path, monkeypatch) -> None:
    repo_root = tmp_path
    (repo_root / ".git" / "hooks").mkdir(parents=True)
    (repo_root / ".themis.backend.yml").write_text(
        "scan:\n  mode: diff\n",
        encoding="utf-8",
    )

    added_lines = "\n".join(f"+line_{idx}" for idx in range(200))
    diff_text = (
        "diff --git a/a.txt b/a.txt\n"
        "--- a/a.txt\n"
        "+++ b/a.txt\n"
        "@@ -0,0 +1,200 @@\n"
        f"{added_lines}\n"
    )
    scan_payload = json.dumps({"findings": []}, ensure_ascii=False)

    call_state = {"n": 0}

    def fake_run(*args, **kwargs):
        call_state["n"] += 1

        class Result:
            pass

        result = Result()
        if call_state["n"] % 2 == 1:
            result.returncode = 0
            result.stdout = diff_text
            result.stderr = ""
        else:
            result.returncode = 0
            result.stdout = scan_payload
            result.stderr = ""
        return result

    monkeypatch.setattr("themis.hooks.run_command", fake_run)

    durations: list[float] = []
    rounds = 30
    for _ in range(rounds):
        started = time.perf_counter()
        code = run_pre_commit_hook(repo_root=repo_root, platform="backend")
        durations.append(time.perf_counter() - started)
        assert code == 0

    p95 = statistics.quantiles(durations, n=100, method="inclusive")[94]
    p99 = statistics.quantiles(durations, n=100, method="inclusive")[98]
    assert p95 <= 1.0
    assert p99 <= 2.0
