import re
from pathlib import Path

from .common import read_text

# Card section headers: "## Name {#anchor}" (anchors vary in prefix)
_SECTION_HDR_RE = re.compile(r"^##\s+(.*?)\s*\{#([A-Za-z0-9][A-Za-z0-9-]*)\}")
# Italic deck line: "_Deck: Middle Republic_"
_DECK_RE = re.compile(r"^_Deck:\s*(.*?)_$")
# Navigation breadcrumb lines to skip
_NAV_LINE_RE = re.compile(r"^\s*\[←")


def parse_misc(filepath: Path) -> dict:
    """Parse misc.md → dict keyed by anchor (e.g. 'bequest-pergamene')."""
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
