import re
import sys
from pathlib import Path

from .tables import parse_markdown_table

# Markdown link in leader table cell: "[Name](#leader-slug)"
_LEADER_CELL_RE = re.compile(r"\[([^\]]+)\]\(#(leader-[A-Za-z0-9-]+)\)")
# Individual leader notes headers: "## Name {#leader-slug}"
_SECTION_HDR_RE = re.compile(r"^##\s+.*\{#(leader-[A-Za-z0-9-]+)\}")


def _int_or_none(s: str) -> int | None:
    try:
        return int(s.strip().lstrip("+"))
    except ValueError:
        return None


def parse_leaders(filepath: Path) -> dict:
    """Parse leaders.md → dict keyed by leader slug (e.g. 'hannibal')."""
    try:
        text = filepath.read_text(encoding="utf-8")
    except OSError as e:
        print(f"  Warning: could not read {filepath}: {e}", file=sys.stderr)
        return {}

    leaders: dict = {}
    lines = text.splitlines()

    # --- Pass 1: summary table ---
    # Columns: Deck | Leader | Strength | Disaster | Standoff
    in_meta = False
    pipe_lines: list[str] = []
    for line in lines:
        if "{#leader-meta}" in line:
            in_meta = True
            continue
        if in_meta:
            if line.startswith("##"):
                break
            if line.strip().startswith("|"):
                pipe_lines.append(line)

    for row in parse_markdown_table(pipe_lines):
        m = _LEADER_CELL_RE.search(row["leader"])
        if not m:
            continue
        name, anchor = m.group(1), m.group(2)
        slug = anchor[len("leader-"):]
        leaders[slug] = {
            "name": name,
            "deck": row["deck"],
            "strength": _int_or_none(row["strength"]),
            "disaster": _int_or_none(row["disaster"]),
            "standoff": _int_or_none(row["standoff"]),
        }

    # --- Pass 2: individual section notes ---
    current_slug: str | None = None
    current_lines: list[str] = []

    def _flush_notes() -> None:
        nonlocal current_slug, current_lines
        if current_slug and current_slug in leaders:
            notes = [
                l.strip()[2:].strip()
                for l in current_lines
                if l.strip().startswith("- ")
            ]
            if notes:
                leaders[current_slug]["notes"] = notes
        current_slug = None
        current_lines = []

    for line in lines:
        m = _SECTION_HDR_RE.match(line)
        if m:
            _flush_notes()
            current_slug = m.group(1)[len("leader-") :]
            continue
        if current_slug is not None:
            current_lines.append(line)

    _flush_notes()
    return leaders
