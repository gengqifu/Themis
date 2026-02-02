import pytest

from themis.gitlab_mr import classify_gitlab_error, validate_diff_text


def test_classify_gitlab_error_for_permission_issue() -> None:
    error_type = classify_gitlab_error(PermissionError("403 forbidden"))
    assert error_type == "permission_denied"


def test_classify_gitlab_error_for_network_issue() -> None:
    error_type = classify_gitlab_error(OSError("connection reset"))
    assert error_type == "network_error"


def test_classify_gitlab_error_for_api_failure() -> None:
    error_type = classify_gitlab_error(RuntimeError("gitlab api failed"))
    assert error_type == "api_failed"


def test_validate_diff_text_rejects_empty_diff() -> None:
    with pytest.raises(ValueError, match="MR diff is empty"):
        validate_diff_text("")

    with pytest.raises(ValueError, match="MR diff is empty"):
        validate_diff_text("   \n\t")


def test_validate_diff_text_accepts_non_empty_diff() -> None:
    result = validate_diff_text("diff --git a/a.txt b/a.txt")
    assert result == "diff --git a/a.txt b/a.txt"
