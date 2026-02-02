from pathlib import Path

from themis.mr_integration import run_mr_scan_job_safe


class FakeGitLabClientE2E:
    def __init__(self, *, diff_text: str) -> None:
        self.diff_text = diff_text
        self.created = []

    def get_mr_diff_text(self, *, project_id: str, merge_request_iid: str) -> str:
        return self.diff_text

    def list_mr_discussions(self, *, project_id: str, merge_request_iid: str):
        return []

    def update_discussion_note(
        self,
        *,
        project_id: str,
        merge_request_iid: str,
        discussion_id: str,
        note_id: int,
        body: str,
    ) -> None:
        raise AssertionError("unexpected update in this e2e test")

    def create_mr_discussion(
        self, *, project_id: str, merge_request_iid: str, body: str
    ) -> None:
        self.created.append((project_id, merge_request_iid, body))


def test_mr_integration_e2e_with_mock_gitlab_and_ci_env(tmp_path: Path) -> None:
    target = tmp_path / "a.txt"
    target.write_text("line1\nBEGIN RSA PRIVATE KEY\n", encoding="utf-8")

    diff_text = """diff --git a/a.txt b/a.txt
--- a/a.txt
+++ b/a.txt
@@ -1,1 +1,2 @@
 line1
+BEGIN RSA PRIVATE KEY
"""
    fake_client = FakeGitLabClientE2E(diff_text=diff_text)
    env = {
        "CI_PIPELINE_SOURCE": "merge_request_event",
        "CI_PROJECT_ID": "100",
        "CI_MERGE_REQUEST_IID": "7",
        "CI_API_V4_URL": "https://gitlab.example/api/v4",
        "GITLAB_TOKEN": "token",
    }

    code = run_mr_scan_job_safe(
        platform="backend",
        paths=[str(tmp_path)],
        repo_root=str(tmp_path),
        env=env,
        client_factory=lambda **_: fake_client,
    )

    assert code == 0
    assert len(fake_client.created) == 1
    body = fake_client.created[0][2]
    assert "<!-- themis:mr-scan -->" in body
    assert "PRIVATE_KEY_BLOCK" in body
    assert "BEGIN RSA PRIVATE KEY" not in body
