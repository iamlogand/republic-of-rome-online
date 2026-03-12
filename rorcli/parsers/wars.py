import re
from pathlib import Path

from .common import collect_bullets, extract_meta_table_lines, int_or_none, read_text
from .tables import parse_markdown_table

# Markdown link in war table cell: "[Name](#war-slug)"
_WAR_CELL_RE = re.compile(r"\[([^\]]+)\]\(#(war-[A-Za-z0-9-]+)\)")
# Individual war notes headers: "## Name {#war-slug}"
_SECTION_HDR_RE = re.compile(r"^##\s+.*\{#(war-[A-Za-z0-9-]+)\}")



def _standoff(s: str) -> list[int] | None:
    """'15' → [15], '11, 14' → [11, 14], '—' → None."""
    s = s.strip()
    if s in ("—", "-", ""):
        return None
    parts = [p.strip() for p in s.split(",")]
    try:
        return [int(p) for p in parts]
    except ValueError:
        return None


def parse_wars(filepath: Path) -> dict:
    """Parse wars.md → dict keyed by war slug (e.g. '1st-gallic')."""
    text = read_text(filepath)
    if text is None:
        return {}

    wars: dict = {}
    lines = text.splitlines()

    # --- Pass 1: summary table ---
    pipe_lines = extract_meta_table_lines(lines, "war")

    for row in parse_markdown_table(pipe_lines):
        m = _WAR_CELL_RE.search(row["war"])
        if not m:
            continue
        name, anchor = m.group(1), m.group(2)
        slug = anchor[len("war-"):]
        series = row["series"].strip()
        wars[slug] = {
            "name": name,
            "deck": row["deck"],
            "series": series if series not in ("—", "-", "") else None,
            "drought": row["drought"].strip().lower() == "yes",
            "land": int_or_none(row["land"]),
            "fleet_support": int_or_none(row["fleet"]),
            "naval": int_or_none(row["naval"]),
            "disaster": int_or_none(row["disaster"]),
            "standoff": _standoff(row["standoff"]),
            "spoils": row["spoils"] if row["spoils"] not in ("—", "-", "") else None,
        }

    # --- Pass 2: individual section notes ---
    current_slug: str | None = None
    current_lines: list[str] = []

    def _flush_notes() -> None:
        nonlocal current_slug, current_lines
        if current_slug and current_slug in wars:
            notes = collect_bullets(current_lines)
            if notes:
                wars[current_slug]["notes"] = notes
        current_slug = None
        current_lines = []

    for line in lines:
        m = _SECTION_HDR_RE.match(line)
        if m:
            _flush_notes()
            current_slug = m.group(1)[len("war-") :]
            continue
        if current_slug is not None:
            current_lines.append(line)

    _flush_notes()
    return wars
