import re
from pathlib import Path

from .common import read_text

_SECTION_HDR_RE = re.compile(r"^#{2,3}\s+(.*?)\s*\{#(concession-[A-Za-z0-9-]+)\}")

_INCOME_TURN_RE = re.compile(r"(\d+)T\s*/\s*Turn", re.IGNORECASE)
_INCOME_COLLECT_RE = re.compile(r"Immediately collect (\d+)T (.+)", re.IGNORECASE)

_INDESTRUCTIBLE_RE = re.compile(r"Cannot be Destroyed", re.IGNORECASE)
_FRAGILE_RE = re.compile(
    r"Destroyed on a (\d+) on 1d6 as a result of (.+)", re.IGNORECASE
)
_DESTROYED_BY_RE = re.compile(r"Destroyed by (.+)", re.IGNORECASE)
_MAY_DESTROY_RE = re.compile(r"May be destroyed by (.+)", re.IGNORECASE)

_RETURN_CURIA_RE = re.compile(r"Return to Curia if (.+)", re.IGNORECASE)
_RETURN_FORUM_RE = re.compile(r"Return to Forum if (.+)", re.IGNORECASE)


def parse_concessions(filepath: Path) -> dict:
    text = read_text(filepath)
    if text is None:
        return {}

    result: dict = {}
    current_slug: str | None = None
    current_name: str = ""
    current_lines: list[str] = []

    def _flush() -> None:
        nonlocal current_slug, current_name, current_lines
        if current_slug is None:
            return

        card: dict = {"name": current_name}
        notes: list[str] = []

        for line in current_lines:
            line = line.strip()
            if not line.startswith("- "):
                continue
            bullet = line[2:].strip().rstrip(".")

            m = _INCOME_TURN_RE.match(bullet)
            if m:
                card["income"] = f"{m.group(1)}T / Turn"
                card["income_amount"] = int(m.group(1))
                continue

            m = _INCOME_COLLECT_RE.match(bullet)
            if m:
                card["income"] = f"{m.group(1)}T {m.group(2)}"
                card["income_amount"] = int(m.group(1))
                continue

            if _INDESTRUCTIBLE_RE.search(bullet):
                card["indestructible"] = True
                continue

            m = _FRAGILE_RE.match(bullet)
            if m:
                card["fragility_die"] = int(m.group(1))
                card.setdefault("destroyed_by", []).append(m.group(2).strip())
                continue

            m = _DESTROYED_BY_RE.match(bullet)
            if m:
                card.setdefault("destroyed_by", []).append(m.group(1).strip())
                continue

            m = _MAY_DESTROY_RE.match(bullet)
            if m:
                card["may_be_destroyed_by"] = m.group(1).strip()
                continue

            m = _RETURN_CURIA_RE.match(bullet)
            if m:
                card["return_curia_if"] = m.group(1).strip()
                continue

            m = _RETURN_FORUM_RE.match(bullet)
            if m:
                card["return_forum_if"] = m.group(1).strip()
                continue

            notes.append(bullet)

        if notes:
            card["notes"] = notes
        result[current_slug] = card
        current_slug = None
        current_name = ""
        current_lines = []

    for line in text.splitlines():
        m = _SECTION_HDR_RE.match(line)
        if m:
            _flush()
            current_name = m.group(1).strip()
            current_slug = m.group(2)[len("concession-"):]
            current_lines = []
            continue
        if current_slug is not None:
            current_lines.append(line)

    _flush()
    return result
