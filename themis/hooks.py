from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Sequence


THEMIS_MARKER = "# themis:managed-pre-commit"
PRE_COMMIT_NAME = "pre-commit"
BACKUP_NAME = "pre-commit.themis.bak"


def _hooks_dir(repo_root: Path) -> Path:
    return repo_root / ".git" / "hooks"


def _build_hook_script(*, platform: str, backup_name: str | None) -> str:
    lines = [
        "#!/bin/sh",
        THEMIS_MARKER,
        'HOOKS_DIR="$(dirname "$0")"',
        'DIFF_FILE="$(mktemp -t themis-diff.XXXXXX)"',
        'git diff --cached -U0 --no-color > "$DIFF_FILE"',
        'themis scan --platform '
        + platform
        + ' --diff-file "$DIFF_FILE"',
        "themis_exit=$?",
        'rm -f "$DIFF_FILE"',
        "if [ $themis_exit -ne 0 ]; then",
        "  exit $themis_exit",
        "fi",
    ]
    if backup_name:
        lines.extend(
            [
                f'"$HOOKS_DIR/{backup_name}"',
                "backup_exit=$?",
                "if [ $backup_exit -ne 0 ]; then",
                "  exit $backup_exit",
                "fi",
            ]
        )
    lines.append("exit 0")
    return "\n".join(lines) + "\n"


def install_hooks(*, repo_root: Path, platform: str) -> None:
    hooks_dir = _hooks_dir(repo_root)
    hooks_dir.mkdir(parents=True, exist_ok=True)
    pre_commit = hooks_dir / PRE_COMMIT_NAME
    backup = hooks_dir / BACKUP_NAME

    if pre_commit.exists():
        current = pre_commit.read_text(encoding="utf-8")
        if THEMIS_MARKER in current:
            return
        if not backup.exists():
            pre_commit.replace(backup)
        script = _build_hook_script(platform=platform, backup_name=BACKUP_NAME)
    else:
        script = _build_hook_script(platform=platform, backup_name=None)

    pre_commit.write_text(script, encoding="utf-8")
    pre_commit.chmod(0o755)


def uninstall_hooks(*, repo_root: Path) -> None:
    hooks_dir = _hooks_dir(repo_root)
    pre_commit = hooks_dir / PRE_COMMIT_NAME
    backup = hooks_dir / BACKUP_NAME
    if not pre_commit.exists():
        return

    current = pre_commit.read_text(encoding="utf-8")
    if THEMIS_MARKER not in current:
        return

    if backup.exists():
        pre_commit.unlink()
        backup.replace(pre_commit)
    else:
        pre_commit.unlink()


def run_command(argv: Sequence[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(argv),
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=False,
    )


def run_pre_commit_hook(*, repo_root: Path, platform: str) -> int:
    git_dir = repo_root / ".git"
    if not git_dir.exists():
        print(
            "Themis hook failed: not a git repository.",
            file=sys.stderr,
            flush=True,
        )
        return 2

    diff_result = run_command(
        ["git", "diff", "--cached", "-U0", "--no-color"],
        cwd=repo_root,
    )
    if diff_result.returncode != 0:
        print(
            "Themis hook failed: failed to read staged diff.",
            file=sys.stderr,
            flush=True,
        )
        return 2
    diff_text = diff_result.stdout
    if not diff_text.strip():
        print(
            "Themis hook failed: staged diff is empty.",
            file=sys.stderr,
            flush=True,
        )
        return 2

    tmp_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", delete=False, prefix="themis-diff-", suffix=".patch"
        ) as tmp:
            tmp.write(diff_text)
            tmp_path = tmp.name

        scan_result = run_command(
            ["themis", "scan", "--platform", platform, "--diff-file", tmp_path],
            cwd=repo_root,
        )
        if scan_result.returncode != 0:
            print(
                "Themis hook failed: scan failed.",
                file=sys.stderr,
                flush=True,
            )
            return scan_result.returncode
        return 0
    finally:
        if tmp_path:
            Path(tmp_path).unlink(missing_ok=True)
