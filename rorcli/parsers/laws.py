import re
import sys
from pathlib import Path

from rorcli.parsers.tables import parse_markdown_table

# Individual law headers: "## Name {#law-slug}"
_LAW_HDR_RE = re.compile(r"^##\s+(.*?)\s*\{#(law-[A-Za-z0-9-]+)\}")
# Table section header
_TABLE_HDR_RE = re.compile(r"^##\s+.*\{#law-meta\}")
# Anchor link in table cell: "[Text](#anchor)" → "anchor"
_ANCHOR_RE = re.compile(r"\(#([^)]+)\)")

_DECK_TO_ERA = {
    "Middle Republic": "middle",
    "Late Republic": "late",
}


def _parse_body(section_lines: list[str]) -> dict:
    """Extract free-text bullet lines as 'text' from a law's body."""
    parts = [line.strip("- ").strip() for line in section_lines if line.strip().startswith("-")]
    result: dict = {}
    if parts:
        result["text"] = " ".join(parts)
    return result


def parse_laws(filepath: Path) -> dict:
    """Parse laws.md → dict keyed by law slug (e.g. 'gabinian')."""
    try:
        text = filepath.read_text(encoding="utf-8")
    except OSError as e:
        print(f"  Warning: could not read {filepath}: {e}", file=sys.stderr)
        return {}

    lines = text.splitlines()

    # --- Pass 1: collect deck info from the summary table ---
    slug_to_deck: dict[str, str] = {}
    in_table = False
    table_lines: list[str] = []
    for line in lines:
        if _TABLE_HDR_RE.match(line):
            in_table = True
            continue
        if in_table:
            if line.strip().startswith("|"):
                table_lines.append(line)
            elif table_lines:
                break  # table ended

    for row in parse_markdown_table(table_lines):
        law_cell = row.get("law", "")
        deck_cell = row.get("deck", "").strip()
        anchor_m = _ANCHOR_RE.search(law_cell)
        if anchor_m:
            slug = anchor_m.group(1)[len("law-"):]  # strip "law-" prefix
            slug_to_deck[slug] = deck_cell

    # --- Pass 2: parse individual law sections ---
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
            current_slug = None  # don't collect table body as a law
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
