from __future__ import annotations

import argparse
from typing import List, Optional

from .config import load_config


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
    load_config(config_path=args.config, platform=args.platform, cwd=None)
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "scan":
        return cmd_scan(args)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
