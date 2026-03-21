import re
from pathlib import Path

from rorcli.parsers.common import collect_bullets, extract_meta_table_lines, read_text
from rorcli.parsers.tables import parse_markdown_table

_LAW_HDR_RE = re.compile(r"^##\s+(.*?)\s*\{#(law-[A-Za-z0-9-]+)\}")
_TABLE_HDR_RE = re.compile(r"^##\s+.*\{#law-meta\}")
_ANCHOR_RE = re.compile(r"\(#([^)]+)\)")

_DECK_TO_ERA = {
    "Middle Republic": "middle",
    "Late Republic": "late",
}


def _parse_body(section_lines: list[str]) -> dict:
    parts = collect_bullets(section_lines)
    result: dict = {}
    if parts:
        result["text"] = " ".join(parts)
    return result


def parse_laws(filepath: Path) -> dict:
    text = read_text(filepath)
    if text is None:
        return {}

    lines = text.splitlines()

    slug_to_deck: dict[str, str] = {}
    table_lines = extract_meta_table_lines(lines, "law")

    for row in parse_markdown_table(table_lines):
        law_cell = row.get("law", "")
        deck_cell = row.get("deck", "").strip()
        anchor_m = _ANCHOR_RE.search(law_cell)
        if anchor_m:
            slug = anchor_m.group(1)[len("law-"):]
            slug_to_deck[slug] = deck_cell

    laws: dict = {}
    current_slug: str | None = None
    current_name: str = ""
    current_lines: list[str] = []

    def _flush() -> None:
        nonlocal current_slug, current_name, current_lines
        if current_slug:
            deck_str = slug_to_deck.get(current_slug, "")
            era = _DECK_TO_ERA.get(deck_str)
            fields = _parse_body(current_lines)
            laws[current_slug] = {
                "name": current_name,
                **({"era": era} if era else {}),
                **({"deck": deck_str} if deck_str else {}),
                **fields,
            }
        current_slug = None
        current_name = ""
        current_lines = []

    for line in lines:
        if _TABLE_HDR_RE.match(line):
            current_slug = None
            continue

        law_m = _LAW_HDR_RE.match(line)
        if law_m:
            _flush()
            current_name = law_m.group(1).strip()
            current_slug = law_m.group(2)[len("law-"):]
            continue

        if current_slug is not None:
            current_lines.append(line)

    _flush()
    return laws
