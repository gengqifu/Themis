from __future__ import annotations

import os
import sys
from typing import Callable, Iterable, Mapping, Optional

from themis.ci_context import ensure_merge_request_pipeline, parse_mr_context
from themis.config import load_config
from themis.diff_utils import parse_unified_diff
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

    def _has_file_headers(text: str) -> bool:
        return "diff --git " in text or "\n+++ " in text or text.startswith("+++ ")

    diff_text: Optional[str] = None
    primary_error: Optional[Exception] = None
    if context.diff_url:
        try:
            diff_text = client.get_diff_text_from_url(url=context.diff_url)
            if not _has_file_headers(diff_text):
                print("themis MR scan: CI diff missing headers, fallback to API diff")
                diff_text = None
                primary_error = RuntimeError(
                    "MR diff from CI URL missing file headers"
                )
        except Exception as exc:
            primary_error = exc

    if diff_text is None:
        try:
            diff_text = client.get_mr_diff_text(
                project_id=context.project_id,
                merge_request_iid=context.merge_request_iid,
            )
        except Exception as fallback_error:
            if primary_error is not None:
                raise RuntimeError(
                    "Failed to get MR diff from CI URL and GitLab API: "
                    f"{primary_error}; {fallback_error}"
                ) from fallback_error
            raise

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
