from themis.allowlist import is_ignored_by_path


def test_path_allowlist() -> None:
    patterns = ["*.log", "secrets/*.txt"]
    assert is_ignored_by_path("a.log", patterns)
    assert is_ignored_by_path("secrets/a.txt", patterns)
    assert not is_ignored_by_path("src/app.py", patterns)
