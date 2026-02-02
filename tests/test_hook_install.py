from pathlib import Path

from themis.hooks import install_hooks


def _read_pre_commit(repo_root: Path) -> str:
    return (repo_root / ".git" / "hooks" / "pre-commit").read_text(encoding="utf-8")


def test_install_hooks_creates_pre_commit_when_missing(tmp_path: Path) -> None:
    repo_root = tmp_path
    hooks_dir = repo_root / ".git" / "hooks"
    hooks_dir.mkdir(parents=True)

    install_hooks(repo_root=repo_root, platform="android")

    content = _read_pre_commit(repo_root)
    assert "themis scan" in content
    assert "--platform android" in content


def test_install_hooks_is_idempotent(tmp_path: Path) -> None:
    repo_root = tmp_path
    hooks_dir = repo_root / ".git" / "hooks"
    hooks_dir.mkdir(parents=True)

    install_hooks(repo_root=repo_root, platform="backend")
    first = _read_pre_commit(repo_root)
    install_hooks(repo_root=repo_root, platform="backend")
    second = _read_pre_commit(repo_root)

    assert first == second
    assert second.count("themis scan") == 1


def test_install_hooks_merges_existing_pre_commit_with_backup(tmp_path: Path) -> None:
    repo_root = tmp_path
    hooks_dir = repo_root / ".git" / "hooks"
    hooks_dir.mkdir(parents=True)
    pre_commit = hooks_dir / "pre-commit"
    pre_commit.write_text("#!/bin/sh\necho old-hook\n", encoding="utf-8")

    install_hooks(repo_root=repo_root, platform="ios")

    backup = hooks_dir / "pre-commit.themis.bak"
    assert backup.exists()
    assert "old-hook" in backup.read_text(encoding="utf-8")

    merged = _read_pre_commit(repo_root)
    assert "--platform ios" in merged
    assert "pre-commit.themis.bak" in merged


def test_install_hooks_merged_script_executes_themis_before_backup(tmp_path: Path) -> None:
    repo_root = tmp_path
    hooks_dir = repo_root / ".git" / "hooks"
    hooks_dir.mkdir(parents=True)
    (hooks_dir / "pre-commit").write_text("#!/bin/sh\necho old\n", encoding="utf-8")

    install_hooks(repo_root=repo_root, platform="web")

    merged = _read_pre_commit(repo_root)
    themis_idx = merged.find("themis scan")
    backup_idx = merged.find("pre-commit.themis.bak")
    assert themis_idx != -1
    assert backup_idx != -1
    assert themis_idx < backup_idx


def test_install_hooks_merged_script_short_circuits_on_themis_failure(tmp_path: Path) -> None:
    repo_root = tmp_path
    hooks_dir = repo_root / ".git" / "hooks"
    hooks_dir.mkdir(parents=True)
    (hooks_dir / "pre-commit").write_text("#!/bin/sh\necho old\n", encoding="utf-8")

    install_hooks(repo_root=repo_root, platform="backend")

    merged = _read_pre_commit(repo_root)
    assert "if [ $themis_exit -ne 0 ]; then" in merged
    assert "exit $themis_exit" in merged
