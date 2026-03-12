import re
from pathlib import Path

from .common import collect_bullets, extract_meta_table_lines, read_text
from .tables import parse_markdown_table

_CARD_CELL_RE = re.compile(r"\[([^\]]+)\]\(#(intrigue-[A-Za-z0-9-]+)\)")
_SECTION_HDR_RE = re.compile(r"^#{2,3}\s+.*\{#(intrigue-[A-Za-z0-9-]+)\}")


def _count(s: str) -> int:
    s = s.strip()
    if s in ("—", "-", ""):
        return 0
    try:
        return int(s)
    except ValueError:
        return 0


def parse_intrigue(filepath: Path) -> dict:
    """Parse intrigue.md → dict keyed by card slug (e.g. 'assassin')."""
    text = read_text(filepath)
    if text is None:
        return {}

    cards: dict = {}
    lines = text.splitlines()

    # --- Pass 1: counts table ---
    # Columns: Card | Early | Middle | Late
    pipe_lines = extract_meta_table_lines(lines, "intrigue")

    for row in parse_markdown_table(pipe_lines):
        m = _CARD_CELL_RE.search(row["card"])
        if not m:
            continue
        name, anchor = m.group(1), m.group(2)
        slug = anchor[len("intrigue-"):]
        cards[slug] = {
            "name": name,
            "count_early": _count(row["early"]),
            "count_middle": _count(row["middle"]),
            "count_late": _count(row["late"]),
        }

    # --- Pass 2: individual section descriptions ---
    current_slug: str | None = None
    current_lines: list[str] = []

    def _flush() -> None:
        nonlocal current_slug, current_lines
        if current_slug and current_slug in cards:
            notes = collect_bullets(current_lines)
            if notes:
                cards[current_slug]["notes"] = notes
        current_slug = None
        current_lines = []

    for line in lines:
        m = _SECTION_HDR_RE.match(line)
        if m:
            _flush()
            anchor = m.group(1)
            current_slug = (
                None if anchor == "intrigue-meta" else anchor[len("intrigue-") :]
            )
            continue
        if current_slug is not None:
            current_lines.append(line)

    _flush()
    return cards
