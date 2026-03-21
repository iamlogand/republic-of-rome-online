import re
from pathlib import Path

from .common import read_text

_SECTION_HDR_RE = re.compile(r"^##\s+(.*?)\s*\{#([A-Za-z0-9][A-Za-z0-9-]*)\}")
_DECK_RE = re.compile(r"^_Deck:\s*(.*?)_$")
_NAV_LINE_RE = re.compile(r"^\s*\[←")


def parse_misc(filepath: Path) -> dict:
    text = read_text(filepath)
    if text is None:
        return {}

    cards: dict = {}
    lines = text.splitlines()
    current_slug: str | None = None
    current_name: str = ""
    current_lines: list[str] = []

    def _flush() -> None:
        nonlocal current_slug, current_name, current_lines
        if current_slug:
            deck: str | None = None
            notes: list[str] = []
            for ln in current_lines:
                stripped = ln.strip()
                if not stripped:
                    continue
                m = _DECK_RE.match(stripped)
                if m:
                    deck = m.group(1).strip()
                    continue
                if stripped.startswith("- "):
                    notes.append(stripped[2:].strip())
            entry: dict = {"name": current_name}
            if deck is not None:
                entry["deck"] = deck
            if notes:
                entry["notes"] = notes
            cards[current_slug] = entry
        current_slug = None
        current_name = ""
        current_lines = []

    for line in lines:
        if _NAV_LINE_RE.match(line):
            continue
        m = _SECTION_HDR_RE.match(line)
        if m:
            _flush()
            current_name = m.group(1).strip()
            current_slug = m.group(2)
            continue
        if current_slug is not None:
            current_lines.append(line)

    _flush()
    return cards
