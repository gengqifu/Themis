import pytest

from themis.ci_context import (
    choose_mr_diff_source,
    ensure_merge_request_pipeline,
    is_merge_request_pipeline,
    parse_mr_context,
)


def test_is_merge_request_pipeline_true() -> None:
    assert is_merge_request_pipeline({"CI_PIPELINE_SOURCE": "merge_request_event"})


def test_is_merge_request_pipeline_false() -> None:
    assert not is_merge_request_pipeline({"CI_PIPELINE_SOURCE": "push"})


def test_ensure_merge_request_pipeline_raises_for_non_mr_source() -> None:
    with pytest.raises(ValueError):
        ensure_merge_request_pipeline({"CI_PIPELINE_SOURCE": "push"})


def test_parse_mr_context_reads_required_variables() -> None:
    env = {
        "CI_PROJECT_ID": "100",
        "CI_MERGE_REQUEST_IID": "7",
        "CI_API_V4_URL": "https://gitlab.example/api/v4",
        "GITLAB_TOKEN": "token",
        "CI_MERGE_REQUEST_DIFF_URL": "https://gitlab.example/diff.patch",
    }
    context = parse_mr_context(env)
    assert context.project_id == "100"
    assert context.merge_request_iid == "7"
    assert context.api_v4_url == "https://gitlab.example/api/v4"
    assert context.gitlab_token == "token"
    assert context.diff_url == "https://gitlab.example/diff.patch"


def test_parse_mr_context_requires_all_mandatory_variables() -> None:
    with pytest.raises(ValueError) as exc_info:
        parse_mr_context({"CI_PROJECT_ID": "100"})
    assert str(exc_info.value) == (
        "Missing required CI variables: CI_API_V4_URL, CI_MERGE_REQUEST_IID, GITLAB_TOKEN"
    )


def test_choose_mr_diff_source_prefers_ci_diff_url() -> None:
    context = parse_mr_context(
        {
            "CI_PROJECT_ID": "100",
            "CI_MERGE_REQUEST_IID": "7",
            "CI_API_V4_URL": "https://gitlab.example/api/v4",
            "GITLAB_TOKEN": "token",
            "CI_MERGE_REQUEST_DIFF_URL": "https://gitlab.example/diff.patch",
        }
    )
    source = choose_mr_diff_source(context=context, diff_file="local.diff")
    assert source.kind == "url"
    assert source.value == "https://gitlab.example/diff.patch"


def test_choose_mr_diff_source_falls_back_to_diff_file() -> None:
    context = parse_mr_context(
        {
            "CI_PROJECT_ID": "100",
            "CI_MERGE_REQUEST_IID": "7",
            "CI_API_V4_URL": "https://gitlab.example/api/v4",
            "GITLAB_TOKEN": "token",
        }
    )
    source = choose_mr_diff_source(context=context, diff_file="local.diff")
    assert source.kind == "file"
    assert source.value == "local.diff"
