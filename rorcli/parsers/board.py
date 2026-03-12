import re
import sys
from pathlib import Path

from rorcli.parsers.tables import parse_markdown_table

# Board section headers: "## Title {#board-slug}"
_SECTION_HDR_RE = re.compile(r"^##\s+(.*?)\s*\{#(board-[A-Za-z0-9-]+)\}")
# Navigation breadcrumb lines to skip
_NAV_LINE_RE = re.compile(r"^\s*\[←")


def _parse_bullet_tree(lines: list[str]) -> list:
    """Parse indented bullet lines into a nested list.

    Each leaf becomes a plain string.
    Each node with children becomes {"text": ..., "items": [...]}.
    Indentation is normalised so the shallowest bullets are level 0.
    """
    # Collect (raw_indent, text) pairs
    parsed: list[tuple[int, str]] = []
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("- "):
            continue
        indent = len(line) - len(line.lstrip())
        parsed.append((indent, stripped[2:].strip()))

    if not parsed:
        return []

    # Normalise indent values to a compact 0-based ranking
    levels = sorted(set(ind for ind, _ in parsed))
    rank = {lv: i for i, lv in enumerate(levels)}
    parsed = [(rank[ind], text) for ind, text in parsed]

    # Stack-based tree construction
    root: list = []
    # stack entries: (level, child_list_of_this_node)
    stack: list[tuple[int, list]] = [(-1, root)]

    for level, text in parsed:
        # Pop until we find a parent strictly shallower than this level
        while len(stack) > 1 and stack[-1][0] >= level:
            stack.pop()
        node: dict = {"text": text, "items": []}
        stack[-1][1].append(node)
        stack.append((level, node["items"]))

    # Remove empty "items" lists, converting leaf dicts to plain strings
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
    """Split section body lines into tables, items (bullet tree), notes, and footnotes."""
    tables: list[list[dict]] = []
    notes: list[str] = []
    bullet_lines: list[str] = []  # raw lines, indentation preserved
    footnotes: list[str] = []

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        # Footnote: line starting with \* (escaped asterisk in Markdown)
        if stripped.startswith("\\*"):
            footnotes.append(stripped.lstrip("\\").lstrip("*").strip())
            i += 1
            continue

        # Table block: collect all consecutive pipe rows
        if stripped.startswith("|"):
            table_lines: list[str] = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i])
                i += 1
            rows = parse_markdown_table(table_lines)
            if rows:
                tables.append(rows)
            continue

        # Bullet line (any indentation level)
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
    """Parse board.md → dict keyed by section slug (e.g. 'combat')."""
    try:
        text = filepath.read_text(encoding="utf-8")
    except OSError as e:
        print(f"  Warning: could not read {filepath}: {e}", file=sys.stderr)
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
            current_slug = m.group(2)[len("board-") :]
            continue
        if current_slug is not None:
            current_lines.append(line)

    _flush()
    return sections
