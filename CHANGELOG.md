# Changelog

All notable changes to this project will be documented in this file.

The format is based on *Keep a Changelog* and the project follows a pragmatic form of semantic versioning.



## [0.1.0] - 2026-01-17

### Added
- Convert FastNotepad exports to Obsidian-ready Markdown (one note per file).
- Parse FastNotepad multi-block export format (`index` preview + `_<id>` full text).
- CLI options:
  - `--by-category` to write notes into category subfolders
  - `--tag` to add `fastnotepad` + category tag
  - `--dry-run` to plan outputs without writing files
  - `--no-frontmatter` to write plain Markdown
  - `--encoding` to force input encoding
- Filename collision handling with ` (2)`, ` (3)`, ...
- Anonymized example dataset and pytest-based test suite.
