from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import List, Optional

from .config import load_config
from .diff_source import choose_diff_source, read_diff_text
from .diff_utils import build_lines_map_from_diff
from .exit_codes import compute_exit_code
from .hooks import install_hooks, uninstall_hooks
from .report import to_json, to_text
from .rules import SEVERITY_ORDER
from .scanner import scan_paths


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="themis")
    sub = parser.add_subparsers(dest="command", required=True)

    scan = sub.add_parser("scan", help="scan repository for sensitive info")
    scan.add_argument("paths", nargs="*", help="paths to scan (default: cwd)")
    scan.add_argument("--platform", required=False, help="platform config to use")
    scan.add_argument("--config", required=False, help="explicit config path")
    scan.add_argument(
        "--format", choices=["text", "json"], default="text", help="output format"
    )
    scan.add_argument("--diff-file", required=False, help="unified diff file path")

    install = sub.add_parser("install-hooks", help="install git pre-commit hook")
    install.add_argument("--platform", required=True, help="platform config to use")
    install.add_argument(
        "--repo-root", required=False, default=".", help="repository root"
    )

    uninstall = sub.add_parser("uninstall-hooks", help="uninstall git pre-commit hook")
    uninstall.add_argument(
        "--repo-root", required=False, default=".", help="repository root"
    )
    return parser


def cmd_scan(args: argparse.Namespace) -> int:
    cfg = load_config(config_path=args.config, platform=args.platform, cwd=None)
    paths = args.paths if args.paths else ["."]
    only_lines = None
    if cfg.get("scan", {}).get("mode") == "diff":
        source = choose_diff_source(
            ci_merge_request_diff_url=os.environ.get("CI_MERGE_REQUEST_DIFF_URL"),
            diff_file=args.diff_file,
        )
        diff_text = read_diff_text(source)
        only_lines = build_lines_map_from_diff(diff_text, repo_root=os.getcwd())
    findings = scan_paths(
        paths,
        rules=cfg.get("rules", []),
        max_file_size_bytes=cfg.get("scan", {}).get("max_file_size_bytes", 0),
        only_lines=only_lines,
        allowlist_paths=cfg.get("allowlist", {}).get("paths", []),
    )
    if args.format == "json":
        print(to_json(findings, redact_keep=cfg.get("output", {}).get("redact_keep", 2)))
    else:
        print(to_text(findings, redact_keep=cfg.get("output", {}).get("redact_keep", 2)))
    threshold = str(cfg.get("scan", {}).get("block_on_severity", "critical")).lower()
    if threshold not in SEVERITY_ORDER:
        threshold = "critical"
    return compute_exit_code(findings, block_threshold=threshold, error=False)


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "scan":
        return cmd_scan(args)
    if args.command == "install-hooks":
        install_hooks(repo_root=Path(args.repo_root), platform=args.platform)
        return 0
    if args.command == "uninstall-hooks":
        uninstall_hooks(repo_root=Path(args.repo_root))
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
