from __future__ import annotations

import argparse
import sys

from . import __version__
from .converter import convert


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description="Convert a FastNotepad export into Obsidian Markdown files.",
    )

    ap.add_argument(
        "export_file",
        help='Export file, e.g. "FastNotepad_2026-01-05"',
    )
    ap.add_argument(
        "output_dir",
        help="Directory to write .md files into",
    )

    ap.add_argument(
        "--by-category",
        action="store_true",
        help="Create subfolders per category",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and plan output files but do not write anything",
    )
    ap.add_argument(
        "--tag",
        action="store_true",
        help="Add Obsidian tags (fastnotepad + category) instead of relying only on category field",
    )
    ap.add_argument(
        "--no-frontmatter",
        action="store_true",
        help="Do not write YAML front matter. If --tag is set, a '#tag' line is prepended.",
    )
    ap.add_argument(
        "--encoding",
        default=None,
        help="Force input file encoding (e.g. utf-8, utf-16, latin-1). If omitted, common encodings are tried.",
    )
    ap.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    return ap


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        result = convert(
            args.export_file,
            args.output_dir,
            by_category=args.by_category,
            dry_run=args.dry_run,
            tag_mode=args.tag,
            no_frontmatter=args.no_frontmatter,
            encoding=args.encoding,
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2

    if args.dry_run:
        print(f"DRY RUN: would write {len(result.planned)} files into: {args.output_dir}")
    else:
        print(f"Wrote {result.written} files into: {args.output_dir}")

    print(f"Prefix/header before JSON: {result.prefix}")

    if result.warnings:
        print(f"Warnings: {len(result.warnings)}")
        for msg in result.warnings[:10]:
            print(" - " + msg)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
