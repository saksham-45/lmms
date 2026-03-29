#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

import pdfplumber


def extract_toc_entries(pdf_path: Path) -> list[tuple[str, int]]:
    entries: list[tuple[str, int]] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        # The LMMS 0.4.12 manual TOC is on pages 3-7 (1-indexed).
        for page_index in range(2, min(7, len(pdf.pages))):
            text = pdf.pages[page_index].extract_text() or ""
            for raw_line in text.splitlines():
                line = raw_line.strip()
                match = re.match(r"^(.*?)\.{2,}\s*([0-9]+)\s*$", line)
                if not match:
                    continue
                title = match.group(1).strip()
                page_num = int(match.group(2))
                entries.append((title, page_num))
    return entries


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract TOC entries from LMMS PDF manual")
    parser.add_argument("--pdf", required=True, help="path to manual PDF")
    parser.add_argument("--out", required=True, help="path to output markdown file")
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    out_path = Path(args.out)

    entries = extract_toc_entries(pdf_path)
    lines = [
        "# Extracted TOC",
        "",
        f"Source: `{pdf_path}`",
        "",
        "| Page | Section |",
        "|---:|---|",
    ]
    for title, page_num in entries:
        safe_title = title.replace("|", "\\|")
        lines.append(f"| {page_num} | {safe_title} |")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {len(entries)} entries to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
