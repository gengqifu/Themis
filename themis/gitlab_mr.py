from __future__ import annotations

import json
from typing import Dict, Iterable, List, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from themis.report import redact
from themis.diff_utils import build_lines_map_from_diff
from themis.scanner import scan_paths


DISCUSSION_ANCHOR = "<!-- themis:mr-scan -->"


def classify_gitlab_error(error: Exception) -> str:
    if isinstance(error, ValueError):
        message = str(error).lower()
        if "missing required ci variables" in message:
            return "missing_variable"
        if "pipeline is not merge_request_event" in message:
            return "invalid_pipeline"
    if isinstance(error, PermissionError):
        return "permission_denied"
    if isinstance(error, OSError):
        return "network_error"
    return "api_failed"


def validate_diff_text(diff_text: str) -> str:
    if not diff_text.strip():
        raise ValueError("MR diff is empty")
    return diff_text


def format_scan_discussion_body(
    findings: Iterable[Dict], *, redact_keep: int = 2, limit: int = 50
) -> str:
    finding_list = list(findings)
    total = len(finding_list)
    show_count = min(total, max(0, limit))
    lines: List[str] = [f"Total findings: {total}"]
    if total > show_count:
        lines.append(f"Showing first {show_count} findings.")

    for finding in finding_list[:show_count]:
        preview = redact(finding.get("match"), keep=redact_keep)
        lines.append(
            "- {severity} {rule_id} {file}:{line} {message} {preview}".format(
                severity=finding.get("severity", ""),
                rule_id=finding.get("rule_id", ""),
                file=finding.get("file", ""),
                line=finding.get("line", 0),
                message=finding.get("message", ""),
                preview=preview,
            ).strip()
        )
    return "\n".join(lines)


def build_mr_scan_output(
    *,
    paths: Iterable[str],
    config: Dict,
    diff_text: str,
    repo_root: str,
) -> str:
    valid_diff = validate_diff_text(diff_text)
    only_lines = build_lines_map_from_diff(valid_diff, repo_root=repo_root)
    findings = scan_paths(
        paths,
        rules=config.get("rules", []),
        max_file_size_bytes=config.get("scan", {}).get("max_file_size_bytes", 0),
        only_lines=only_lines,
        allowlist_paths=config.get("allowlist", {}).get("paths", []),
    )
    output_cfg = config.get("output", {})
    return format_scan_discussion_body(
        findings,
        redact_keep=output_cfg.get("redact_keep", 2),
        limit=output_cfg.get("max_discussion_findings", 50),
    )


def upsert_scan_discussion(
    *, client, project_id: str, merge_request_iid: str, content: str
) -> None:
    body = f"{DISCUSSION_ANCHOR}\n{content}"
    discussions = client.list_mr_discussions(
        project_id=project_id, merge_request_iid=merge_request_iid
    )
    for discussion in discussions:
        discussion_id = str(discussion.get("id", ""))
        for note in discussion.get("notes", []):
            note_body = note.get("body", "")
            if DISCUSSION_ANCHOR in note_body:
                client.update_discussion_note(
                    project_id=project_id,
                    merge_request_iid=merge_request_iid,
                    discussion_id=discussion_id,
                    note_id=int(note["id"]),
                    body=body,
                )
                return
    client.create_mr_discussion(
        project_id=project_id, merge_request_iid=merge_request_iid, body=body
    )


class GitLabApiClient:
    def __init__(
        self, *, api_v4_url: str, token: str, timeout_seconds: int = 15
    ) -> None:
        self.api_v4_url = api_v4_url.rstrip("/")
        self.token = token
        self.timeout_seconds = timeout_seconds

    def _request_json(self, *, method: str, path: str, payload: Optional[Dict] = None):
        url = f"{self.api_v4_url}{path}"
        data = None
        headers = {"PRIVATE-TOKEN": self.token}
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        req = Request(url=url, method=method, headers=headers, data=data)
        try:
            with urlopen(req, timeout=self.timeout_seconds) as resp:
                body = resp.read().decode("utf-8")
                if not body:
                    return None
                return json.loads(body)
        except HTTPError as error:
            if error.code in (401, 403):
                raise PermissionError(str(error)) from error
            raise RuntimeError(f"GitLab API request failed: {error.code}") from error
        except URLError as error:
            raise OSError(f"GitLab network error: {error.reason}") from error

    def list_mr_discussions(self, *, project_id: str, merge_request_iid: str):
        project = quote(project_id, safe="")
        path = f"/projects/{project}/merge_requests/{merge_request_iid}/discussions"
        return self._request_json(method="GET", path=path) or []

    def create_mr_discussion(
        self, *, project_id: str, merge_request_iid: str, body: str
    ) -> None:
        project = quote(project_id, safe="")
        path = f"/projects/{project}/merge_requests/{merge_request_iid}/discussions"
        self._request_json(method="POST", path=path, payload={"body": body})

    def update_discussion_note(
        self,
        *,
        project_id: str,
        merge_request_iid: str,
        discussion_id: str,
        note_id: int,
        body: str,
    ) -> None:
        project = quote(project_id, safe="")
        path = (
            f"/projects/{project}/merge_requests/{merge_request_iid}/discussions/"
            f"{discussion_id}/notes/{note_id}"
        )
        self._request_json(method="PUT", path=path, payload={"body": body})

    def get_mr_diff_text(self, *, project_id: str, merge_request_iid: str) -> str:
        project = quote(project_id, safe="")
        path = f"/projects/{project}/merge_requests/{merge_request_iid}/changes"
        data = self._request_json(method="GET", path=path) or {}
        changes = data.get("changes", [])
        parts: List[str] = []
        for change in changes:
            diff = change.get("diff")
            if diff:
                parts.append(diff)
        return validate_diff_text("\n".join(parts))
