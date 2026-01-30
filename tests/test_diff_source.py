import pytest

from themis.diff_source import choose_diff_source


def test_choose_diff_source_prefers_ci_url() -> None:
    src = choose_diff_source(ci_merge_request_diff_url="http://x", diff_file="d.patch")
    assert src.kind == "url"
    assert src.value == "http://x"


def test_choose_diff_source_uses_file_when_no_url() -> None:
    src = choose_diff_source(ci_merge_request_diff_url=None, diff_file="d.patch")
    assert src.kind == "file"
    assert src.value == "d.patch"


def test_choose_diff_source_requires_input() -> None:
    with pytest.raises(ValueError):
        choose_diff_source(ci_merge_request_diff_url=None, diff_file=None)
