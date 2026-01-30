from pathlib import Path

from themis.file_utils import is_binary_bytes, is_binary_file, is_too_large


def test_is_binary_bytes() -> None:
    assert is_binary_bytes(b"hello") is False
    assert is_binary_bytes(b"\x00\x01") is True


def test_is_binary_file(tmp_path: Path) -> None:
    text_file = tmp_path / "a.txt"
    text_file.write_text("hello", encoding="utf-8")
    assert is_binary_file(text_file) is False

    bin_file = tmp_path / "a.bin"
    bin_file.write_bytes(b"\x00\x01\x02")
    assert is_binary_file(bin_file) is True


def test_is_too_large(tmp_path: Path) -> None:
    f = tmp_path / "big.txt"
    f.write_text("abcd", encoding="utf-8")
    assert is_too_large(f, max_file_size_bytes=3) is True
    assert is_too_large(f, max_file_size_bytes=10) is False
