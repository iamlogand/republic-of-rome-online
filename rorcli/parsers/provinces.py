import re
import sys
from pathlib import Path

from .tables import parse_markdown_table

# Markdown link in province table cell: "[Name](#province-slug)"
_PROVINCE_CELL_RE = re.compile(r"\[([^\]]+)\]\(#(province-[A-Za-z0-9-]+)\)")
# Individual province section headers: "## Name {#province-slug}"
_SECTION_HDR_RE = re.compile(r"^##\s+.*\{#(province-[A-Za-z0-9-]+)\}")
# Taxes column value (e.g. "20T")
_TAXES_RE = re.compile(r"(\d+)T")
# Province note fields in individual sections
_CREATED_BY_RE = re.compile(r"Created by:\s*(.+)")
_DEFENDS_RE = re.compile(r"Defends:\s*(.+)")

# Meta anchor to skip when scanning for individual province sections
_META_ANCHOR = "province-meta"


def _int_or_none(s: str) -> int | None:
    s = s.strip()
    if s in ("—", "-", ""):
        return None
    try:
        return int(s)
    except ValueError:
        return None


def _taxes(s: str) -> int | None:
    """'20T' → 20."""
    m = _TAXES_RE.match(s.strip())
    return int(m.group(1)) if m else None


def _stats(row: dict, key: str) -> dict:
    """Extract province stats from a parsed table row."""
    return {
        "spoils": row["spoils"] if row["spoils"] not in ("—", "-", "") else None,
        "state": row["state"] if row["state"] not in ("—", "-", "") else None,
        "taxes": _taxes(row["taxes"]),
        "land_base": _int_or_none(row["land_base"]),
        "land_max": _int_or_none(row["land_max"]),
        "naval_base": _int_or_none(row["naval_base"]),
        "naval_max": _int_or_none(row["naval_max"]),
    }


def _parse_tables(lines: list[str]) -> tuple[dict, dict]:
    """
    Parse both province tables from within the {#province-meta} section.
    Tables are distinguished by their header row: "Undeveloped Province" vs "Developed Province".
    Returns (undeveloped_dict, developed_dict), each keyed by province slug.
    """
    undeveloped: dict = {}
    developed: dict = {}

    in_meta = False
    pipe_lines: list[str] = []

    for line in lines:
        if "{#province-meta}" in line:
            in_meta = True
            continue
        if in_meta:
            if line.startswith("##"):
                break
            if line.strip().startswith("|"):
                pipe_lines.append(line)

    # Split pipe_lines into undeveloped and developed groups at the "Developed Province" header
    split_idx = next(
        (
            i for i, l in enumerate(pipe_lines)
            if "Developed" in l.strip().strip("|").split("|")[0]
        ),
        len(pipe_lines),
    )
    u_rows = parse_markdown_table(pipe_lines[:split_idx])
    d_rows = parse_markdown_table(pipe_lines[split_idx:])

    for row in u_rows:
        m = _PROVINCE_CELL_RE.search(row["undeveloped_province"])
        if not m:
            continue
        name, anchor = m.group(1), m.group(2)
        slug = anchor[len("province-"):]
        undeveloped[slug] = {"name": name, **_stats(row, "undeveloped_province")}

    for row in d_rows:
        m = _PROVINCE_CELL_RE.search(row["developed_province"])
        if not m:
            continue
        name, anchor = m.group(1), m.group(2)
        slug = anchor[len("province-"):]
        developed[slug] = {"name": name, **_stats(row, "developed_province")}

    return undeveloped, developed


def parse_provinces(filepath: Path) -> dict:
    """Parse provinces.md → dict keyed by province slug (e.g. 'africa')."""
    try:
        text = filepath.read_text(encoding="utf-8")
    except OSError as e:
        print(f"  Warning: could not read {filepath}: {e}", file=sys.stderr)
        return {}

    lines = text.splitlines()
    undeveloped, developed = _parse_tables(lines)

    # Merge: each province gets undeveloped/developed sub-dicts
    provinces: dict = {}
    for slug in set(undeveloped) | set(developed):
        u = undeveloped.get(slug, {})
        d = developed.get(slug, {})
        name = u.get("name") or d.get("name") or slug.replace("-", " ").title()
        provinces[slug] = {
            "name": name,
            "undeveloped": {k: v for k, v in u.items() if k != "name"},
            "developed": {k: v for k, v in d.items() if k != "name"},
        }

    # --- Individual section notes ---
    current_slug: str | None = None
    current_lines: list[str] = []

    def _flush_notes() -> None:
        nonlocal current_slug, current_lines
        if current_slug and current_slug in provinces:
            notes: list[str] = []
            for l in current_lines:
                l = l.strip()
                if not l.startswith("- "):
                    continue
                bullet = l[2:].strip()
                if bullet == "Frontier Province":
                    provinces[current_slug]["frontier"] = True
                    continue
                m = _CREATED_BY_RE.match(bullet)
                if m:
                    provinces[current_slug]["created_by"] = m.group(1).strip()
                    continue
                m = _DEFENDS_RE.match(bullet)
                if m:
                    provinces[current_slug]["defends"] = m.group(1).strip()
                    continue
                notes.append(bullet)
            if notes:
                provinces[current_slug]["notes"] = notes
        current_slug = None
        current_lines = []

    for line in lines:
        m = _SECTION_HDR_RE.match(line)
        if m:
            _flush_notes()
            anchor = m.group(1)
            current_slug = (
                None if anchor == _META_ANCHOR else anchor[len("province-") :]
            )
            continue
        if current_slug is not None:
            current_lines.append(line)

    _flush_notes()
    return provinces
