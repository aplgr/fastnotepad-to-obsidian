# Examples

This directory contains a small sanitized export (`sample_export`).

Run conversion into a temporary directory:

```bash
python3 ../scripts/fastnotepad2obsidian.py sample_export /tmp/FastNotepad_Imported --by-category
```

Try variants:

```bash
python3 ../scripts/fastnotepad2obsidian.py sample_export /tmp/FastNotepad_Imported --dry-run
python3 ../scripts/fastnotepad2obsidian.py sample_export /tmp/FastNotepad_Imported --tag
python3 ../scripts/fastnotepad2obsidian.py sample_export /tmp/FastNotepad_Imported --no-frontmatter --tag
python3 ../scripts/fastnotepad2obsidian.py sample_export /tmp/FastNotepad_Imported --encoding utf-8
```
