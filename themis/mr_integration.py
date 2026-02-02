from __future__ import annotations

import os
import sys
from typing import Callable, Iterable, Mapping, Optional

from themis.ci_context import ensure_merge_request_pipeline, parse_mr_context
from themis.config import load_config
from themis.gitlab_mr import (
    GitLabApiClient,
    build_mr_scan_output,
    classify_gitlab_error,
    upsert_scan_discussion,
)


def run_mr_scan_job(
    *,
    platform: str = "backend",
    paths: Optional[Iterable[str]] = None,
    repo_root: Optional[str] = None,
    env: Optional[Mapping[str, str]] = None,
    client_factory: Optional[Callable[..., object]] = None,
) -> str:
    ensure_merge_request_pipeline(env)
    context = parse_mr_context(env)
    root = repo_root or os.getcwd()
    scan_paths = list(paths) if paths is not None else [root]

    factory = client_factory or GitLabApiClient
    client = factory(api_v4_url=context.api_v4_url, token=context.gitlab_token)

    diff_text = client.get_mr_diff_text(
        project_id=context.project_id,
        merge_request_iid=context.merge_request_iid,
    )
    config = load_config(platform=platform, cwd=root)
    body = build_mr_scan_output(
        paths=scan_paths,
        config=config,
        diff_text=diff_text,
        repo_root=root,
    )
    upsert_scan_discussion(
        client=client,
        project_id=context.project_id,
        merge_request_iid=context.merge_request_iid,
        content=body,
    )
    return body


def run_mr_scan_job_safe(
    *,
    platform: str = "backend",
    paths: Optional[Iterable[str]] = None,
    repo_root: Optional[str] = None,
    env: Optional[Mapping[str, str]] = None,
    client_factory: Optional[Callable[..., object]] = None,
) -> int:
    try:
        run_mr_scan_job(
            platform=platform,
            paths=paths,
            repo_root=repo_root,
            env=env,
            client_factory=client_factory,
        )
        print("themis MR scan completed")
        return 0
    except Exception as exc:
        print(
            f"themis MR scan failed: {classify_gitlab_error(exc)} - {exc}",
            file=sys.stderr,
        )
        return 2
