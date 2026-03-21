import re
from pathlib import Path

from .common import collect_bullets, extract_meta_table_lines, read_text
from .tables import parse_markdown_table

_STATESMAN_CELL_RE = re.compile(
    r"\[(\d+[A-Za-z]+)\s+[—-]\s+([^\]]+)\]\(#statesman-([A-Za-z0-9-]+)\)"
)
_FAMILY_NUM_RE = re.compile(r"#(\d+)")
_SECTION_HDR_RE = re.compile(r"^##\s+.*\{#statesman-([A-Za-z0-9-]+)\}")
_SPECIAL_RE = re.compile(r"^-\s+Special:\s*(.+)")


def _int_or_val(s: str) -> int | str | None:
    s = s.strip()
    if s in ("—", "-", ""):
        return None
    try:
        return int(s)
    except ValueError:
        return s


def parse_statesmen(filepath: Path) -> dict:
    text = read_text(filepath)
    if text is None:
        return {}

    statesmen: dict = {}
    lines = text.splitlines()

    pipe_lines = extract_meta_table_lines(lines, "statesman")

    for row in parse_markdown_table(pipe_lines):
        m = _STATESMAN_CELL_RE.search(row["statesman"])
        if not m:
            continue
        id = m.group(1)
        name = m.group(2).strip()
        slug = m.group(3)

        fam_m = _FAMILY_NUM_RE.search(row["family"])
        family = int(fam_m.group(1)) if fam_m else None

        conflicts_raw = row["conflicts"].strip()
        conflicts = (
            None
            if conflicts_raw in ("—", "-", "")
            else [c.strip() for c in conflicts_raw.split(",")]
        )

        statesmen[slug] = {
            "id": id,
            "name": name,
            "deck": row["deck"].strip(),
            "family": family,
            "m": _int_or_val(row["mil"]),
            "o": _int_or_val(row["ora"]),
            "l": _int_or_val(row["loy"]),
            "conflicts": conflicts,
            "i": _int_or_val(row["inf"]),
            "pop": _int_or_val(row["pop"]),
        }

    current_slug: str | None = None
    current_lines: list[str] = []

    def _flush() -> None:
        nonlocal current_slug, current_lines
        if current_slug and current_slug in statesmen:
            bullets = collect_bullets(current_lines)
            if bullets:
                special_m = _SPECIAL_RE.match(f"- {bullets[0]}")
                if special_m:
                    statesmen[current_slug]["special"] = special_m.group(1).strip()
                else:
                    statesmen[current_slug]["notes"] = bullets
        current_slug = None
        current_lines = []

    for line in lines:
        m = _SECTION_HDR_RE.match(line)
        if m:
            _flush()
            slug = m.group(1)
            current_slug = slug if slug in statesmen else None
            continue
        if current_slug is not None:
            current_lines.append(line)

    _flush()
    return statesmen
