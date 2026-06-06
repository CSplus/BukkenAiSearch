#!/usr/bin/env python3
"""Generate a Word-openable RTF file from the client design Markdown.

This intentionally writes plain-text RTF rather than binary .docx so Codex/GitHub
PR creation can include the client-facing Word document without binary-file
support.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


HEADING_SIZES = {
    1: 36,
    2: 30,
    3: 26,
    4: 24,
}


def rtf_escape(text: str) -> str:
    """Escape text for RTF using unicode escapes for non-ASCII characters."""
    parts: list[str] = []
    for char in text:
        code = ord(char)
        if char in {"\\", "{", "}"}:
            parts.append("\\" + char)
        elif char == "\t":
            parts.append("\\tab ")
        elif char == "\n":
            parts.append("\\par\n")
        elif 32 <= code <= 126:
            parts.append(char)
        else:
            signed = code if code <= 32767 else code - 65536
            parts.append(f"\\u{signed}?")
    return "".join(parts)


def strip_inline_markdown(text: str) -> str:
    """Convert the small inline Markdown subset used by the docs to plain text."""
    text = text.replace("`", "")
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"__(.*?)__", r"\1", text)
    text = re.sub(r"\[(.*?)\]\((.*?)\)", r"\1 (\2)", text)
    return text


def is_table_separator(line: str) -> bool:
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell or "") for cell in cells)


def table_row(line: str) -> str:
    cells = [strip_inline_markdown(cell.strip()) for cell in line.strip().strip("|").split("|")]
    return " / ".join(cells)


def render_markdown(markdown: str) -> list[str]:
    lines = markdown.splitlines()
    rtf_lines: list[str] = []
    paragraph: list[str] = []

    def flush_paragraph() -> None:
        if not paragraph:
            return
        text = " ".join(part.strip() for part in paragraph if part.strip())
        if text:
            rtf_lines.append(rtf_escape(strip_inline_markdown(text)) + r"\par")
        paragraph.clear()

    for raw_line in lines:
        line = raw_line.rstrip()
        stripped = line.strip()

        if not stripped:
            flush_paragraph()
            rtf_lines.append(r"\par")
            continue

        heading = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if heading:
            flush_paragraph()
            level = len(heading.group(1))
            size = HEADING_SIZES[level]
            text = strip_inline_markdown(heading.group(2))
            rtf_lines.append(rf"\b\fs{size} {rtf_escape(text)}\b0\fs22\par")
            continue

        if stripped.startswith("|") and stripped.endswith("|"):
            flush_paragraph()
            if is_table_separator(stripped):
                continue
            rtf_lines.append(r"\pard\li360 " + rtf_escape(table_row(stripped)) + r"\par")
            continue

        bullet = re.match(r"^[-*]\s+(.*)$", stripped)
        if bullet:
            flush_paragraph()
            text = strip_inline_markdown(bullet.group(1))
            rtf_lines.append(r"\pard\li360\fi-180 \bullet\tab " + rtf_escape(text) + r"\par")
            continue

        numbered = re.match(r"^(\d+)\.\s+(.*)$", stripped)
        if numbered:
            flush_paragraph()
            text = strip_inline_markdown(numbered.group(2))
            rtf_lines.append(rf"\pard\li360\fi-180 {numbered.group(1)}.\tab " + rtf_escape(text) + r"\par")
            continue

        paragraph.append(stripped)

    flush_paragraph()
    return rtf_lines


def generate(input_path: Path, output_path: Path) -> None:
    markdown = input_path.read_text(encoding="utf-8")
    body = "\n".join(render_markdown(markdown))
    rtf = "{\\rtf1\\ansi\\deff0\n{\\fonttbl{\\f0 Yu Gothic;}}\n\\f0\\fs22\n" + body + "\n}\n"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rtf, encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: generate_rtf_from_markdown.py <input.md> <output.rtf>", file=sys.stderr)
        return 2
    generate(Path(sys.argv[1]), Path(sys.argv[2]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
