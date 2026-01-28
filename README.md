# FastNotepad → Obsidian Migrator

[![Tests](https://github.com/aplgr/fastnotepad-to-obsidian/actions/workflows/tests.yml/badge.svg)](https://github.com/aplgr/fastnotepad-to-obsidian/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](../../pulls)

Convert Android **FastNotepad** exports into **Obsidian-ready Markdown** (one note per file).

- One note per `.md` file
- Optional category folders (`--by-category`)
- Optional Obsidian tags (`--tag`)
- Optional YAML front matter (default) or plain Markdown (`--no-frontmatter`)
- Handles the FastNotepad export quirk where the **preview** lives in the `index` block, while the **full note body** is stored separately as `_<id>` keys


## Case study (DE)

If you want the full project context (why this exists, workflow, results), [here's the write-up](https://andreploeger.com/cases/wissensinseln-konsolidiert-obsidian-git-sync?utm_source=github.com&utm_medium=readme).


## Requirements

- Python 3.9+

## Install

### Recommended: pipx (isolated CLI install)

Install directly from GitHub:

```bash
pipx install git+https://github.com/aplgr/fastnotepad-to-obsidian.git
```

### Alternative: pip

```bash
pip install .
```

This installs a CLI command: `fastnotepad2obsidian`.

### No install (run from source)

```bash
python3 scripts/fastnotepad2obsidian.py --help
# or
PYTHONPATH=src python3 -m fastnotepad_to_obsidian --help
```

## Quickstart

```bash
fastnotepad2obsidian FastNotepad_2026-01-05 Vault/Inbox --by-category
```

Dry-run (show what would be created, but write nothing):

```bash
fastnotepad2obsidian FastNotepad_2026-01-05 Vault/Inbox --by-category --dry-run
```

## CLI options

### Dry run

Plan outputs but do not write files:

```bash
fastnotepad2obsidian FastNotepad_2026-01-05 Vault/Inbox --by-category --dry-run
```

### Tags

Add Obsidian tags (always `#fastnotepad` plus the category tag if present):

```bash
fastnotepad2obsidian FastNotepad_2026-01-05 Vault/Inbox --tag
```

With YAML front matter enabled (default), tags are written as:

```yaml
tags: [fastnotepad, work]
```

### No front matter

Write plain Markdown without YAML front matter:

```bash
fastnotepad2obsidian FastNotepad_2026-01-05 Vault/Inbox --no-frontmatter
```

If you combine `--no-frontmatter --tag`, tags are prepended as a regular Obsidian tag line:

```markdown
#fastnotepad #gad-arbeiter

...note content...
```

### Encoding override

If your export file is not detected correctly, force the input encoding:

```bash
fastnotepad2obsidian FastNotepad_2026-01-05 Vault/Inbox --encoding latin-1
```

Supported values depend on Python, e.g.: `utf-8`, `utf-8-sig`, `utf-16`, `utf-16-le`, `latin-1`.

## Output rules

- Filenames are based on the **first non-empty line** of the note content (slugified).
- Collisions are resolved with ` (2)`, ` (3)`, ...
- With `--by-category`, notes are written into subfolders by category (slugified). Empty category becomes `Unsorted`.

## Supported export format

This tool supports the FastNotepad export format that looks like:

- `<prefix>#<json_block_1>{[!*|@]}<json_block_2>{[!*|@]}...`
- `json_block_1` contains `index` with `^!` note records (metadata + preview text)
- Later blocks contain the full texts keyed as `_<id>`

If your app uses a different format, open an issue with a **sanitized** snippet.

## Safety & privacy

- This tool runs locally and does **not** make network requests.
- Your export file may contain highly sensitive data (passwords, addresses, etc.).
  Please do **not** attach real exports to public issues. If you need help, redact the content first.

## Troubleshooting

- **`JSONDecodeError: Extra data`**: Your export has multiple blocks / trailing content. This tool extracts and merges JSON blocks separated by `{[!*|@]}`.
- **Some notes remain short**: Those notes may not have a corresponding `_<id>` full-text entry in the export. The tool will fall back to the preview text from the `index` block.
- **Weird characters**: rerun with `--encoding ...` (e.g. `latin-1`, `utf-16`).

## Contributing

PRs and format samples are welcome.

If you open an issue because your export differs, please include:
- the app name + version
- a **sanitized** export snippet (header + one note record + the `_<id>` mapping)
- the exact command you ran and the output

## Development

Run tests:

```bash
pip install -e .[dev]
pytest
```

## Roadmap (on purpose)

- Improve slugging/filename templates
- More resilient format detection if FastNotepad changes the export structure

## License

MIT
