import re
import sys
from pathlib import Path

from .tables import parse_markdown_table

# Markdown link in war table cell: "[Name](#war-slug)"
_WAR_CELL_RE = re.compile(r"\[([^\]]+)\]\(#(war-[A-Za-z0-9-]+)\)")
# Individual war notes headers: "## Name {#war-slug}"
_SECTION_HDR_RE = re.compile(r"^##\s+.*\{#(war-[A-Za-z0-9-]+)\}")


def _int_or_none(s: str) -> int | None:
    s = s.strip()
    if s in ("—", "-", ""):
        return None
    try:
        return int(s)
    except ValueError:
        return None


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
    try:
        text = filepath.read_text(encoding="utf-8")
    except OSError as e:
        print(f"  Warning: could not read {filepath}: {e}", file=sys.stderr)
        return {}

    wars: dict = {}
    lines = text.splitlines()

    # --- Pass 1: summary table ---
    in_meta = False
    pipe_lines: list[str] = []
    for line in lines:
        if "{#war-meta}" in line:
            in_meta = True
            continue
        if in_meta:
            if line.startswith("##"):
                break
            if line.strip().startswith("|"):
                pipe_lines.append(line)

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
            "land": _int_or_none(row["land"]),
            "fleet_support": _int_or_none(row["fleet"]),
            "naval": _int_or_none(row["naval"]),
            "disaster": _int_or_none(row["disaster"]),
            "standoff": _standoff(row["standoff"]),
            "spoils": row["spoils"] if row["spoils"] not in ("—", "-", "") else None,
        }

    # --- Pass 2: individual section notes ---
    current_slug: str | None = None
    current_lines: list[str] = []

    def _flush_notes() -> None:
        nonlocal current_slug, current_lines
        if current_slug and current_slug in wars:
            notes = [
                l.strip()[2:].strip()
                for l in current_lines
                if l.strip().startswith("- ")
            ]
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
