import re
from pathlib import Path

from .common import collect_bullets, extract_meta_table_lines, int_or_none, read_text
from .tables import parse_markdown_table

_LEADER_CELL_RE = re.compile(r"\[([^\]]+)\]\(#(leader-[A-Za-z0-9-]+)\)")
_SECTION_HDR_RE = re.compile(r"^##\s+.*\{#(leader-[A-Za-z0-9-]+)\}")


def parse_leaders(filepath: Path) -> dict:
    text = read_text(filepath)
    if text is None:
        return {}

    leaders: dict = {}
    lines = text.splitlines()

    pipe_lines = extract_meta_table_lines(lines, "leader")

    for row in parse_markdown_table(pipe_lines):
        m = _LEADER_CELL_RE.search(row["leader"])
        if not m:
            continue
        name, anchor = m.group(1), m.group(2)
        slug = anchor[len("leader-"):]
        leaders[slug] = {
            "name": name,
            "deck": row["deck"],
            "strength": int_or_none(row["strength"], strip_plus=True),
            "disaster": int_or_none(row["disaster"], strip_plus=True),
            "standoff": int_or_none(row["standoff"], strip_plus=True),
        }

    current_slug: str | None = None
    current_lines: list[str] = []

    def _flush_notes() -> None:
        nonlocal current_slug, current_lines
        if current_slug and current_slug in leaders:
            notes = collect_bullets(current_lines)
            if notes:
                leaders[current_slug]["notes"] = notes
        current_slug = None
        current_lines = []

    for line in lines:
        m = _SECTION_HDR_RE.match(line)
        if m:
            _flush_notes()
            current_slug = m.group(1)[len("leader-"):]
            continue
        if current_slug is not None:
            current_lines.append(line)

    _flush_notes()
    return leaders
