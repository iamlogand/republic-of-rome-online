import re
from pathlib import Path

from .common import collect_bullets, read_text

_SECTION_HDR_RE = re.compile(r"^##\s+(.*?)\s*\{#(event-[A-Za-z0-9-]+)\}")
_VARIANT_HDR_RE = re.compile(r"^###\s+Dark blue side:\s*(.+)")


def parse_events(filepath: Path) -> dict:
    text = read_text(filepath)
    if text is None:
        return {}

    events: dict = {}
    current_slug: str | None = None
    current_name: str = ""
    main_lines: list[str] = []
    dark_blue_name: str | None = None
    variant_lines: list[str] = []
    in_variant: bool = False

    def _flush() -> None:
        nonlocal current_slug, current_name, main_lines, dark_blue_name, variant_lines, in_variant
        if current_slug:
            entry: dict = {"name": current_name}
            notes = collect_bullets(main_lines)
            if notes:
                entry["notes"] = notes
            if dark_blue_name is not None:
                dark_blue: dict = {"name": dark_blue_name}
                v_notes = collect_bullets(variant_lines)
                if v_notes:
                    dark_blue["notes"] = v_notes
                entry["dark_blue_side"] = dark_blue
            events[current_slug] = entry
        current_slug = None
        current_name = ""
        main_lines = []
        dark_blue_name = None
        variant_lines = []
        in_variant = False

    for line in text.splitlines():
        m = _SECTION_HDR_RE.match(line)
        if m:
            _flush()
            current_name = m.group(1).strip()
            current_slug = m.group(2)[len("event-"):]
            continue
        if current_slug is None:
            continue
        v = _VARIANT_HDR_RE.match(line)
        if v:
            dark_blue_name = v.group(1).strip()
            in_variant = True
            continue
        if in_variant:
            variant_lines.append(line)
        else:
            main_lines.append(line)

    _flush()
    return events
