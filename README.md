# FastNotepad → Obsidian Migrator

Convert Android **FastNotepad** exports into **Obsidian-ready Markdown**.

- One note per `.md` file
- Optional category folders
- Optional Obsidian tags
- Optional YAML front matter
- Handles the FastNotepad export quirk where the **preview** lives in the `index` block, while the **full note body** is stored separately as `_<id>` keys.

## Requirements

- Python 3.9+

## Install (optional)

```bash
pip install .
```

This installs a CLI command: `fastnotepad2obsidian`.

## Quickstart

```bash
fastnotepad2obsidian FastNotepad_2026-01-05 Vault/Inbox --by-category
```

Or without installation:

```bash
python3 scripts/fastnotepad2obsidian.py FastNotepad_2026-01-05 Vault/Inbox --by-category
# or
PYTHONPATH=src python3 -m fastnotepad_to_obsidian FastNotepad_2026-01-05 Vault/Inbox --by-category
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

Write plain markdown without YAML front matter:

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

## Limitations

- This supports the export format that looks like:
  - `<prefix>#<json_block_1>{[!*|@]}<json_block_2>{[!*|@]}...`
  - `json_block_1` contains `index` with `^!` note records
  - Later blocks contain the full texts keyed as `_<id>`
- If your app uses a different format, open an issue with a **sanitized** snippet.

## Development

Run tests:

```bash
pip install -e .[dev]
pytest
```

## License

MIT
