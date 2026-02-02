from pathlib import Path

from themis.gitlab_mr import DISCUSSION_ANCHOR
from themis.mr_integration import run_mr_scan_job, run_mr_scan_job_safe


class FakeGitLabClient:
    def __init__(self, *, diff_text: str) -> None:
        self.diff_text = diff_text
        self.updated = []

    def get_mr_diff_text(self, *, project_id: str, merge_request_iid: str) -> str:
        return self.diff_text

    def list_mr_discussions(self, *, project_id: str, merge_request_iid: str):
        return [{"id": "d1", "notes": [{"id": 11, "body": DISCUSSION_ANCHOR}]}]

    def update_discussion_note(
        self,
        *,
        project_id: str,
        merge_request_iid: str,
        discussion_id: str,
        note_id: int,
        body: str,
    ) -> None:
        self.updated.append((project_id, merge_request_iid, discussion_id, note_id, body))

    def create_mr_discussion(
        self, *, project_id: str, merge_request_iid: str, body: str
    ) -> None:
        raise AssertionError("should update existing discussion")


def test_run_mr_scan_job_builds_output_and_updates_discussion(tmp_path: Path) -> None:
    target = tmp_path / "a.txt"
    target.write_text("line1\nBEGIN RSA PRIVATE KEY\n", encoding="utf-8")
    diff_text = """diff --git a/a.txt b/a.txt
--- a/a.txt
+++ b/a.txt
@@ -1,1 +1,2 @@
 line1
+BEGIN RSA PRIVATE KEY
"""
    fake_client = FakeGitLabClient(diff_text=diff_text)
    env = {
        "CI_PIPELINE_SOURCE": "merge_request_event",
        "CI_PROJECT_ID": "100",
        "CI_MERGE_REQUEST_IID": "7",
        "CI_API_V4_URL": "https://gitlab.example/api/v4",
        "GITLAB_TOKEN": "token",
    }
    body = run_mr_scan_job(
        platform="backend",
        paths=[str(tmp_path)],
        repo_root=str(tmp_path),
        env=env,
        client_factory=lambda **_: fake_client,
    )
    assert "PRIVATE_KEY_BLOCK" in body
    assert fake_client.updated


def test_run_mr_scan_job_safe_returns_nonzero_on_error(capsys) -> None:
    code = run_mr_scan_job_safe(
        env={"CI_PIPELINE_SOURCE": "merge_request_event"},
    )
    assert code == 2
    err = capsys.readouterr().err
    assert "missing_variable" in err
    assert "Missing required CI variables" in err
