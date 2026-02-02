from themis.gitlab_mr import DISCUSSION_ANCHOR, upsert_scan_discussion


class FakeGitLabClient:
    def __init__(self, discussions):
        self.discussions = discussions
        self.updated = []
        self.created = []

    def list_mr_discussions(self, *, project_id: str, merge_request_iid: str):
        return self.discussions

    def update_discussion_note(
        self,
        *,
        project_id: str,
        merge_request_iid: str,
        discussion_id: str,
        note_id: int,
        body: str,
    ) -> None:
        self.updated.append(
            (project_id, merge_request_iid, discussion_id, note_id, body)
        )

    def create_mr_discussion(
        self, *, project_id: str, merge_request_iid: str, body: str
    ) -> None:
        self.created.append((project_id, merge_request_iid, body))


def test_upsert_scan_discussion_updates_existing_anchored_discussion() -> None:
    client = FakeGitLabClient(
        discussions=[
            {
                "id": "d-1",
                "notes": [
                    {"id": 101, "body": f"old result\n{DISCUSSION_ANCHOR}"},
                ],
            }
        ]
    )
    upsert_scan_discussion(
        client=client,
        project_id="100",
        merge_request_iid="7",
        content="new result",
    )
    assert client.created == []
    assert client.updated == [
        ("100", "7", "d-1", 101, f"{DISCUSSION_ANCHOR}\nnew result")
    ]


def test_upsert_scan_discussion_creates_when_anchor_not_found() -> None:
    client = FakeGitLabClient(
        discussions=[
            {
                "id": "d-2",
                "notes": [{"id": 201, "body": "normal discussion"}],
            }
        ]
    )
    upsert_scan_discussion(
        client=client,
        project_id="100",
        merge_request_iid="7",
        content="scan result",
    )
    assert client.updated == []
    assert client.created == [("100", "7", f"{DISCUSSION_ANCHOR}\nscan result")]
