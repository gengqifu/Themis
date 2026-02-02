from pathlib import Path

from themis.cli import main


def test_cli_install_hooks_calls_install(monkeypatch, tmp_path: Path) -> None:
    called = {}

    def fake_install(*, repo_root: Path, platform: str) -> None:
        called["repo_root"] = repo_root
        called["platform"] = platform

    monkeypatch.setattr("themis.cli.install_hooks", fake_install)
    exit_code = main(
        ["install-hooks", "--platform", "backend", "--repo-root", str(tmp_path)]
    )
    assert exit_code == 0
    assert called["repo_root"] == tmp_path
    assert called["platform"] == "backend"


def test_cli_uninstall_hooks_calls_uninstall(monkeypatch, tmp_path: Path) -> None:
    called = {}

    def fake_uninstall(*, repo_root: Path) -> None:
        called["repo_root"] = repo_root

    monkeypatch.setattr("themis.cli.uninstall_hooks", fake_uninstall)
    exit_code = main(["uninstall-hooks", "--repo-root", str(tmp_path)])
    assert exit_code == 0
    assert called["repo_root"] == tmp_path
