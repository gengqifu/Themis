import pytest

from themis.diff_source import choose_diff_source, read_diff_text


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


def test_read_diff_text_from_file(tmp_path) -> None:
    p = tmp_path / "d.patch"
    p.write_text("diff", encoding="utf-8")
    src = choose_diff_source(ci_merge_request_diff_url=None, diff_file=str(p))
    assert read_diff_text(src) == "diff"
