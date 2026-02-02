from __future__ import annotations

import subprocess
import os
from pathlib import Path

from themis.hooks import run_pre_commit_hook


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _run_git(repo_root: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args],
        cwd=str(repo_root),
        check=True,
        capture_output=True,
        text=True,
    )


def _init_repo(repo_root: Path) -> None:
    _run_git(repo_root, "init")
    _run_git(repo_root, "config", "user.name", "test-user")
    _run_git(repo_root, "config", "user.email", "test@example.com")


def _install_themis_wrapper(bin_dir: Path) -> None:
    wrapper = bin_dir / "themis"
    wrapper.write_text(
        "#!/bin/sh\n"
        f'PYTHONPATH="{PROJECT_ROOT}" exec "{PROJECT_ROOT}/.venv/bin/python" -m themis "$@"\n',
        encoding="utf-8",
    )
    wrapper.chmod(0o755)


def _install_fake_themis_no_findings(bin_dir: Path) -> None:
    wrapper = bin_dir / "themis"
    wrapper.write_text(
        "#!/bin/sh\n"
        "if [ \"$1\" = \"scan\" ]; then\n"
        "  echo '{\"findings\":[]}'\n"
        "  exit 0\n"
        "fi\n"
        "exit 1\n",
        encoding="utf-8",
    )
    wrapper.chmod(0o755)


def test_hook_e2e_blocks_commit_on_critical(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo-critical"
    repo.mkdir()
    _init_repo(repo)

    (repo / ".themis.backend.yml").write_text(
        "scan:\n"
        "  mode: diff\n",
        encoding="utf-8",
    )
    target = repo / "a.txt"
    target.write_text("BEGIN RSA PRIVATE KEY\n", encoding="utf-8")
    _run_git(repo, "add", "a.txt", ".themis.backend.yml")

    bin_dir = tmp_path / "bin-critical"
    bin_dir.mkdir()
    _install_themis_wrapper(bin_dir)
    old_path = os.environ.get("PATH", "")
    monkeypatch.setenv("PATH", f"{bin_dir}:{old_path}")

    code = run_pre_commit_hook(repo_root=repo, platform="backend")
    assert code == 2


def test_hook_e2e_allows_commit_on_non_critical(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo-high"
    repo.mkdir()
    _init_repo(repo)

    (repo / ".themis.backend.yml").write_text(
        "scan:\n"
        "  mode: diff\n"
        "rules:\n"
        "  - id: HIGH_LEAK\n"
        "    severity: high\n"
        "    type: regex\n"
        "    pattern: LEAK_ME\n"
        "    message: high leak\n"
        "    enabled: true\n",
        encoding="utf-8",
    )
    target = repo / "a.txt"
    target.write_text("LEAK_ME\n", encoding="utf-8")
    _run_git(repo, "add", "a.txt", ".themis.backend.yml")

    bin_dir = tmp_path / "bin-high"
    bin_dir.mkdir()
    _install_themis_wrapper(bin_dir)
    old_path = os.environ.get("PATH", "")
    monkeypatch.setenv("PATH", f"{bin_dir}:{old_path}")

    code = run_pre_commit_hook(repo_root=repo, platform="backend")
    assert code == 0


def test_hook_e2e_allows_commit_when_path_exempted(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo-exempt"
    repo.mkdir()
    _init_repo(repo)

    (repo / ".themis.backend.yml").write_text("scan:\n  mode: diff\n", encoding="utf-8")
    (repo / "secrets").mkdir()
    target = repo / "secrets" / "a.txt"
    target.write_text("LEAK_ME\n", encoding="utf-8")
    _run_git(repo, "add", "secrets/a.txt", ".themis.backend.yml")

    bin_dir = tmp_path / "bin-exempt"
    bin_dir.mkdir()
    _install_fake_themis_no_findings(bin_dir)
    old_path = os.environ.get("PATH", "")
    monkeypatch.setenv("PATH", f"{bin_dir}:{old_path}")

    code = run_pre_commit_hook(repo_root=repo, platform="backend")
    assert code == 0
