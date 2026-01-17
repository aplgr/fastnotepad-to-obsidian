from __future__ import annotations

from pathlib import Path

import pytest

from fastnotepad_to_obsidian.cli import main as cli_main
from fastnotepad_to_obsidian.converter import convert


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def sample_export_path() -> Path:
    return repo_root() / "examples" / "sample_export"


def test_convert_by_category_writes_files(tmp_path: Path) -> None:
    out_dir = tmp_path / "vault"
    result = convert(str(sample_export_path()), str(out_dir), by_category=True)

    assert result.written == 3
    # Ensure something was actually written
    md_files = list(out_dir.rglob("*.md"))
    assert len(md_files) == 3


def test_dry_run_writes_nothing(tmp_path: Path) -> None:
    out_dir = tmp_path / "vault"
    result = convert(str(sample_export_path()), str(out_dir), dry_run=True)

    assert result.written == 0
    assert len(result.planned) == 3
    assert not out_dir.exists()


def test_tag_mode_adds_tags_in_frontmatter(tmp_path: Path) -> None:
    out_dir = tmp_path / "vault"
    convert(str(sample_export_path()), str(out_dir), tag_mode=True)

    md_files = sorted(out_dir.rglob("*.md"))
    assert md_files

    text = md_files[0].read_text(encoding="utf-8")
    assert text.startswith("---")
    assert "tags: [fastnotepad" in text


def test_no_frontmatter_with_tags_prepends_tag_line(tmp_path: Path) -> None:
    out_dir = tmp_path / "vault"
    convert(
        str(sample_export_path()),
        str(out_dir),
        no_frontmatter=True,
        tag_mode=True,
    )

    md_files = sorted(out_dir.rglob("*.md"))
    assert md_files

    text = md_files[0].read_text(encoding="utf-8")
    assert not text.startswith("---")
    assert text.splitlines()[0].startswith("#fastnotepad")


def test_encoding_override_latin1(tmp_path: Path) -> None:
    # Create a latin-1 encoded export that includes characters like ó/á.
    raw = sample_export_path().read_text(encoding="utf-8")
    export_latin1 = tmp_path / "export_latin1"
    export_latin1.write_bytes(raw.encode("latin-1", errors="strict"))

    out_dir = tmp_path / "vault"
    result = convert(str(export_latin1), str(out_dir), encoding="latin-1")

    assert result.written == 3
    assert len(list(out_dir.rglob("*.md"))) == 3


def test_cli_dry_run_exit_code_and_output(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    out_dir = tmp_path / "vault"
    code = cli_main([str(sample_export_path()), str(out_dir), "--dry-run"])
    captured = capsys.readouterr()

    assert code == 0
    assert "DRY RUN" in captured.out
    assert not out_dir.exists()
