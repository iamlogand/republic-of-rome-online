import re
from pathlib import Path

from .common import int_or_none, read_text
from .tables import parse_markdown_table

_PROVINCE_CELL_RE = re.compile(r"\[([^\]]+)\]\(#(province-[A-Za-z0-9-]+)\)")
_SECTION_HDR_RE = re.compile(r"^##\s+.*\{#(province-[A-Za-z0-9-]+)\}")
_TAXES_RE = re.compile(r"(\d+)T")
_CREATED_BY_RE = re.compile(r"Created by:\s*(.+)")
_DEFENDS_RE = re.compile(r"Defends:\s*(.+)")

_META_ANCHOR = "province-meta"


def _taxes(s: str) -> int | None:
    m = _TAXES_RE.match(s.strip())
    return int(m.group(1)) if m else None


def _stats(row: dict, key: str) -> dict:
    return {
        "spoils": row["spoils"] if row["spoils"] not in ("—", "-", "") else None,
        "state": row["state"] if row["state"] not in ("—", "-", "") else None,
        "taxes": _taxes(row["taxes"]),
        "land_base": int_or_none(row["land_base"]),
        "land_max": int_or_none(row["land_max"]),
        "naval_base": int_or_none(row["naval_base"]),
        "naval_max": int_or_none(row["naval_max"]),
    }


def _parse_tables(lines: list[str]) -> tuple[dict, dict]:
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
    text = read_text(filepath)
    if text is None:
        return {}

    lines = text.splitlines()
    undeveloped, developed = _parse_tables(lines)

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
                None if anchor == _META_ANCHOR else anchor[len("province-"):]
            )
            continue
        if current_slug is not None:
            current_lines.append(line)

    _flush_notes()
    return provinces
