import re
from pathlib import Path

from rorcli.parsers.common import read_text
from rorcli.parsers.tables import parse_markdown_table

_SECTION_HDR_RE = re.compile(r"^##\s+(.*?)\s*\{#(board-[A-Za-z0-9-]+)\}")
_NAV_LINE_RE = re.compile(r"^\s*\[←")


def _parse_bullet_tree(lines: list[str]) -> list:
    parsed: list[tuple[int, str]] = []
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("- "):
            continue
        indent = len(line) - len(line.lstrip())
        parsed.append((indent, stripped[2:].strip()))

    if not parsed:
        return []

    levels = sorted(set(ind for ind, _ in parsed))
    rank = {lv: i for i, lv in enumerate(levels)}
    parsed = [(rank[ind], text) for ind, text in parsed]

    root: list = []
    stack: list[tuple[int, list]] = [(-1, root)]

    for level, text in parsed:
        while len(stack) > 1 and stack[-1][0] >= level:
            stack.pop()
        node: dict = {"text": text, "items": []}
        stack[-1][1].append(node)
        stack.append((level, node["items"]))

    def _clean(lst: list) -> list:
        result = []
        for item in lst:
            if item["items"]:
                item["items"] = _clean(item["items"])
                result.append(item)
            else:
                result.append(item["text"])
        return result

    return _clean(root)


def _parse_content(lines: list[str]) -> dict:
    tables: list[list[dict]] = []
    notes: list[str] = []
    bullet_lines: list[str] = []
    footnotes: list[str] = []

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if stripped.startswith("\\*"):
            footnotes.append(re.sub(r"^\\\*", "", stripped).strip())
            i += 1
            continue

        if stripped.startswith("|"):
            table_lines: list[str] = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i])
                i += 1
            rows = parse_markdown_table(table_lines)
            if rows:
                tables.append(rows)
            continue

        if stripped.startswith("- "):
            bullet_lines.append(line)
            i += 1
            continue

        notes.append(stripped)
        i += 1

    result: dict = {}
    if tables:
        result["tables"] = tables
    if bullet_lines:
        result["items"] = _parse_bullet_tree(bullet_lines)
    if notes:
        result["notes"] = notes
    if footnotes:
        result["footnotes"] = footnotes
    return result


def parse_board(filepath: Path) -> dict:
    text = read_text(filepath)
    if text is None:
        return {}

    sections: dict = {}
    current_slug: str | None = None
    current_title: str = ""
    current_lines: list[str] = []

    def _flush() -> None:
        nonlocal current_slug, current_title, current_lines
        if current_slug:
            entry = {"name": current_title, **_parse_content(current_lines)}
            sections[current_slug] = entry
        current_slug = None
        current_title = ""
        current_lines = []

    for line in text.splitlines():
        if _NAV_LINE_RE.match(line):
            continue
        m = _SECTION_HDR_RE.match(line)
        if m:
            _flush()
            current_title = m.group(1).strip()
            current_slug = m.group(2)[len("board-"):]
            continue
        if current_slug is not None:
            current_lines.append(line)

    _flush()
    return sections
