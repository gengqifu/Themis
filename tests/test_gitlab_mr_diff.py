from themis.gitlab_mr import GitLabApiClient


class FakeClient(GitLabApiClient):
    def __init__(self, *, response):
        super().__init__(api_v4_url="http://gitlab/api/v4", token="token")
        self._response = response

    def _request_json(self, *, method: str, path: str, payload=None):
        return self._response


def test_get_mr_diff_text_adds_headers_when_missing() -> None:
    data = {
        "changes": [
            {
                "old_path": "a.txt",
                "new_path": "a.txt",
                "diff": "@@ -0,0 +1 @@\n+BEGIN RSA PRIVATE KEY\n",
            }
        ]
    }
    client = FakeClient(response=data)
    diff = client.get_mr_diff_text(project_id="1", merge_request_iid="2")
    assert "diff --git a/a.txt b/a.txt" in diff
    assert "+++ b/a.txt" in diff
    assert "BEGIN RSA PRIVATE KEY" in diff


def test_get_mr_diff_text_handles_new_file() -> None:
    data = {
        "changes": [
            {
                "old_path": "a.txt",
                "new_path": "a.txt",
                "new_file": True,
                "diff": "@@ -0,0 +1 @@\n+line\n",
            }
        ]
    }
    client = FakeClient(response=data)
    diff = client.get_mr_diff_text(project_id="1", merge_request_iid="2")
    assert "--- a/dev/null" in diff
    assert "+++ b/a.txt" in diff
