from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping, Optional

from themis.diff_source import DiffSource, choose_diff_source


REQUIRED_CI_VARIABLES = (
    "CI_PROJECT_ID",
    "CI_MERGE_REQUEST_IID",
    "CI_API_V4_URL",
    "GITLAB_TOKEN",
)


@dataclass(frozen=True)
class MergeRequestContext:
    project_id: str
    merge_request_iid: str
    api_v4_url: str
    gitlab_token: str
    diff_url: Optional[str]


def parse_mr_context(env: Optional[Mapping[str, str]] = None) -> MergeRequestContext:
    variables = dict(os.environ if env is None else env)
    missing = [name for name in REQUIRED_CI_VARIABLES if not variables.get(name)]
    if missing:
        missing_names = ", ".join(sorted(missing))
        raise ValueError(f"Missing required CI variables: {missing_names}")

    return MergeRequestContext(
        project_id=variables["CI_PROJECT_ID"],
        merge_request_iid=variables["CI_MERGE_REQUEST_IID"],
        api_v4_url=variables["CI_API_V4_URL"],
        gitlab_token=variables["GITLAB_TOKEN"],
        diff_url=variables.get("CI_MERGE_REQUEST_DIFF_URL"),
    )


def choose_mr_diff_source(
    *, context: MergeRequestContext, diff_file: Optional[str]
) -> DiffSource:
    return choose_diff_source(
        ci_merge_request_diff_url=context.diff_url,
        diff_file=diff_file,
    )
