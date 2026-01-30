from __future__ import annotations

import argparse
from typing import List, Optional

from .config import load_config
from .exit_codes import compute_exit_code
from .report import to_json, to_text
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
    return parser


def cmd_scan(args: argparse.Namespace) -> int:
    cfg = load_config(config_path=args.config, platform=args.platform, cwd=None)
    paths = args.paths if args.paths else ["."]
    findings = scan_paths(
        paths,
        rules=cfg.get("rules", []),
        max_file_size_bytes=cfg.get("scan", {}).get("max_file_size_bytes", 0),
    )
    if args.format == "json":
        print(to_json(findings, redact_keep=cfg.get("output", {}).get("redact_keep", 2)))
    else:
        print(to_text(findings, redact_keep=cfg.get("output", {}).get("redact_keep", 2)))
    return compute_exit_code(findings, block_threshold="critical", error=False)


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "scan":
        return cmd_scan(args)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
