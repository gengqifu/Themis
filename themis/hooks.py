from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence

from themis.config import load_config
from themis.exit_codes import compute_exit_code
from themis.rules import SEVERITY_ORDER

THEMIS_MARKER = "# themis:managed-pre-commit"
PRE_COMMIT_NAME = "pre-commit"
BACKUP_NAME = "pre-commit.themis.bak"
FAILED_PREFIX = "Themis hook failed:"


def _hooks_dir(repo_root: Path) -> Path:
    return repo_root / ".git" / "hooks"


def _pre_commit_paths(repo_root: Path) -> tuple[Path, Path]:
    hooks_dir = _hooks_dir(repo_root)
    return hooks_dir / PRE_COMMIT_NAME, hooks_dir / BACKUP_NAME


def _emit_error(message: str) -> None:
    print(f"{FAILED_PREFIX} {message}", file=sys.stderr, flush=True)


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
    pre_commit, backup = _pre_commit_paths(repo_root)

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
    pre_commit, backup = _pre_commit_paths(repo_root)
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


def resolve_block_on_severity(
    *, cli_value: str | None, config: Mapping[str, Any]
) -> str:
    if cli_value:
        value = cli_value.lower()
    else:
        scan_cfg = config.get("scan", {})
        if isinstance(scan_cfg, Mapping):
            raw = scan_cfg.get("block_on_severity")
            value = str(raw).lower() if raw else "critical"
        else:
            value = "critical"
    if value not in SEVERITY_ORDER:
        raise ValueError(f"Invalid block_on_severity: {value}")
    return value


def _collect_staged_diff(repo_root: Path) -> str | None:
    diff_result = run_command(
        ["git", "diff", "--cached", "-U0", "--no-color"],
        cwd=repo_root,
    )
    if diff_result.returncode != 0:
        _emit_error("failed to read staged diff.")
        return None
    diff_text = diff_result.stdout
    if not diff_text.strip():
        _emit_error("staged diff is empty.")
        return None
    return diff_text


def _run_scan_with_diff_file(
    *, repo_root: Path, platform: str, diff_text: str
) -> tuple[int, list[dict[str, Any]] | None]:
    tmp_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", delete=False, prefix="themis-diff-", suffix=".patch"
        ) as tmp:
            tmp.write(diff_text)
            tmp_path = tmp.name

        scan_result = run_command(
            [
                "themis",
                "scan",
                "--platform",
                platform,
                "--diff-file",
                tmp_path,
                "--format",
                "json",
            ],
            cwd=repo_root,
        )
        if scan_result.returncode not in (0, 2):
            _emit_error("scan failed.")
            return 1, None
        raw_stdout = scan_result.stdout.strip()
        if not raw_stdout:
            raise ValueError("Empty scan output")
        payload = json.loads(raw_stdout)
        findings = payload.get("findings", [])
        if not isinstance(findings, list):
            raise ValueError("Invalid findings format")
        return 0, findings
    except Exception:
        _emit_error("scan output parse failed.")
        return 1, None
    finally:
        if tmp_path:
            Path(tmp_path).unlink(missing_ok=True)


def run_pre_commit_hook(
    *, repo_root: Path, platform: str, block_on_severity: str | None = None
) -> int:
    git_dir = repo_root / ".git"
    if not git_dir.exists():
        _emit_error("not a git repository.")
        return 1

    diff_text = _collect_staged_diff(repo_root)
    if diff_text is None:
        return 1

    try:
        cfg = load_config(platform=platform, cwd=str(repo_root))
        threshold = resolve_block_on_severity(
            cli_value=block_on_severity,
            config=cfg,
        )
        scan_error, findings = _run_scan_with_diff_file(
            repo_root=repo_root,
            platform=platform,
            diff_text=diff_text,
        )
        if scan_error != 0 or findings is None:
            return 1
        return compute_exit_code(findings, block_threshold=threshold, error=False)
    except ValueError as exc:
        _emit_error(str(exc))
        return 1
