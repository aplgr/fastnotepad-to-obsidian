from __future__ import annotations

import datetime as dt
import json
import os
import re
import unicodedata
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

DELIM_NOTE = "^!"
DELIM_BLOCK = "{[!*|@]}"


@dataclass
class ConvertResult:
    """Conversion summary."""

    prefix: str
    written: int
    planned: List[str]
    warnings: List[str]


def read_text(path: str, encoding: Optional[str] = None) -> str:
    """Read a text file with optional forced encoding.

    If encoding is None, try common encodings.
    """

    with open(path, "rb") as f:
        raw = f.read()

    if encoding:
        return raw.decode(encoding)

    for enc in ("utf-8-sig", "utf-8", "utf-16", "utf-16-le", "utf-16-be", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue

    return raw.decode("utf-8", errors="replace")


def safe_slug(s: str, max_len: int = 80) -> str:
    """Create a reasonably filesystem-safe filename slug."""

    s = s.strip()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"[^\w\s\-\.\(\)\[\]]+", "", s, flags=re.UNICODE)
    s = s.strip()
    if not s:
        s = "note"
    if len(s) > max_len:
        s = s[:max_len].rstrip()
    return s


def safe_tag(s: str, max_len: int = 60) -> str:
    """Create an Obsidian-friendly tag token (no spaces)."""

    s = s.strip().lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"[^a-z0-9\-_\/]+", "", s)
    s = s.strip("-_")
    if not s:
        s = "unsorted"
    if len(s) > max_len:
        s = s[:max_len].rstrip("-_")
    return s


def unix_to_iso(ts: str) -> Optional[str]:
    try:
        if ts is None:
            return None
        ts = str(ts).strip()
        if not ts:
            return None
        v = int(float(ts))
        return dt.datetime.fromtimestamp(v).isoformat(timespec="seconds")
    except Exception:
        return None


def first_non_empty_line(text: str) -> str:
    for line in text.splitlines():
        if line.strip():
            return line.strip()
    return ""


def _parse_first_json_object(s: str) -> Dict[str, Any]:
    s = s.strip()
    start = s.find("{")
    if start == -1:
        raise ValueError("Could not find '{' in JSON block.")

    decoder = json.JSONDecoder()
    obj, _end = decoder.raw_decode(s, idx=start)
    if not isinstance(obj, dict):
        raise ValueError("JSON block is not an object/dict.")
    return obj


def parse_export(content: str) -> Tuple[str, Dict[str, Any]]:
    """Parse a FastNotepad export.

    Format:
      <prefix>#<json_block_1>{[!*|@]}<json_block_2>{[!*|@]}...

    Block 1 contains "index" (preview + metadata), and a later block contains
    full note bodies keyed as "_<id>".
    """

    if "#" not in content:
        raise ValueError("Export does not contain '#' separator before JSON payload.")

    prefix, rest = content.split("#", 1)
    prefix = prefix.strip()
    rest = rest.strip()

    merged: Dict[str, Any] = {}

    blocks = [b for b in rest.split(DELIM_BLOCK) if b.strip()]
    if not blocks:
        raise ValueError("No JSON blocks found after '#'.")

    for b in blocks:
        obj = _parse_first_json_object(b)
        merged.update(obj)

    return prefix, merged


def split_notes(index_str: str) -> List[str]:
    parts = index_str.split(DELIM_NOTE)
    return [p for p in parts if p]


def parse_note_record(record: str) -> Dict[str, Any]:
    """Parse a single '^! ...' record from the index."""

    fields = record.split(";", 9)
    if len(fields) < 10:
        raise ValueError(f"Record has unexpected field count ({len(fields)}): {record[:120]}...")

    note_id = fields[0]
    category = fields[1]
    bg_color = fields[2]
    created_unix = fields[3]
    maybe_updated = fields[4]
    text_color = fields[5]
    unknown_num = fields[6]
    maybe_empty2 = fields[7]
    options_raw = fields[8]
    note_text = fields[9]

    options: Dict[str, Any] = {}
    options_raw = options_raw.strip()
    if options_raw:
        try:
            options = json.loads(options_raw)
        except Exception:
            options = {"_raw": options_raw}

    return {
        "id": note_id,
        "category": category.strip(),
        "bg_color": bg_color.strip(),
        "created_unix": created_unix.strip(),
        "updated_unix": maybe_updated.strip(),
        "text_color": text_color.strip(),
        "unknown_num": unknown_num.strip(),
        "unknown_field": maybe_empty2.strip(),
        "options": options,
        "content": note_text.replace("\r\n", "\n").replace("\r", "\n"),
    }


def _escape_yaml_string(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def render_markdown(note_meta: Dict[str, Any], body: str, *, no_frontmatter: bool, tag_mode: bool) -> str:
    """Render markdown with optional YAML front matter and optional tags."""

    category = (note_meta.get("category") or "").strip()

    tags: List[str] = []
    if tag_mode:
        tags.append("fastnotepad")
        if category:
            tags.append(safe_tag(category))

    if no_frontmatter:
        prefix = ""
        if tags:
            prefix = " ".join(f"#{t}" for t in tags) + "\n\n"
        return prefix + body.rstrip() + "\n"

    created_iso = unix_to_iso(note_meta.get("created_unix", ""))
    updated_iso = unix_to_iso(note_meta.get("updated_unix", ""))

    fm: List[str] = ["---"]
    fm.append('source: "FastNotepad"')
    fm.append(f'note_id: "{_escape_yaml_string(str(note_meta.get("id", "")))}"')

    if category:
        fm.append(f'category: "{_escape_yaml_string(category)}"')

    if created_iso:
        fm.append(f"created: {created_iso}")
    if updated_iso:
        fm.append(f"updated: {updated_iso}")

    bg = (note_meta.get("bg_color") or "").strip()
    if bg:
        fm.append(f'bg_color: "{_escape_yaml_string(bg)}"')

    tc = (note_meta.get("text_color") or "").strip()
    if tc:
        fm.append(f'text_color: "{_escape_yaml_string(tc)}"')

    options = note_meta.get("options") or {}
    if isinstance(options, dict) and "reminder" in options:
        fm.append(f"reminder: {options['reminder']}")

    if tags:
        fm.append(f"tags: [{', '.join(tags)}]")

    fm.append("---\n")

    return "\n".join(fm) + body.rstrip() + "\n"


def convert(
    export_file: str,
    output_dir: str,
    *,
    by_category: bool = False,
    dry_run: bool = False,
    tag_mode: bool = False,
    no_frontmatter: bool = False,
    encoding: Optional[str] = None,
) -> ConvertResult:
    """Convert a FastNotepad export into Obsidian Markdown files."""

    raw = read_text(export_file, encoding=encoding).strip()
    prefix, obj = parse_export(raw)

    index_str = obj.get("index")
    if not isinstance(index_str, str):
        raise ValueError("JSON payload does not contain string field 'index'.")

    records = split_notes(index_str)
    if not records:
        raise ValueError("No notes found (index split produced 0 records).")

    planned_paths: List[str] = []
    warnings: List[str] = []
    successes = 0

    # Avoid collisions deterministically within this run
    seen_paths: Dict[str, int] = {}

    def alloc_unique_path(base_path: str) -> str:
        if base_path not in seen_paths:
            seen_paths[base_path] = 1
            return base_path
        seen_paths[base_path] += 1
        root, ext = os.path.splitext(base_path)
        return f"{root} ({seen_paths[base_path]}){ext}"

    for n, rec in enumerate(records, start=1):
        try:
            note = parse_note_record(rec)

            full_key = f"_{note.get('id', '')}"
            full_text = obj.get(full_key)
            if isinstance(full_text, str) and full_text.strip():
                note["content"] = full_text.replace("\r\n", "\n").replace("\r", "\n")

            content = str(note.get("content", ""))
            title_line = first_non_empty_line(content)
            slug = safe_slug(title_line if title_line else f"note-{n}")

            out_dir = output_dir
            if by_category:
                cat = safe_slug(note.get("category") or "Unsorted", max_len=50)
                out_dir = os.path.join(output_dir, cat)

            filename = f"{slug}.md"
            out_path = os.path.join(out_dir, filename)
            out_path = alloc_unique_path(out_path)

            planned_paths.append(out_path)

            if not dry_run:
                os.makedirs(out_dir, exist_ok=True)
                md = render_markdown(note, content, no_frontmatter=no_frontmatter, tag_mode=tag_mode)
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(md)

            successes += 1

        except Exception as e:
            warnings.append(f"[{n}] {e}")

    written = 0 if dry_run else successes

    return ConvertResult(prefix=prefix, written=written, planned=planned_paths, warnings=warnings)
