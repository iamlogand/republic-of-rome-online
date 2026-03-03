"""
Build step: parse all Markdown rulebook files → rorcli/rorcli.db.json

Schema
------
{
  "meta": { "built_at", "rules_dir", "total_sections", "total_glossary_terms" },
  "sections": {
    "<id>": {
      "id": str,          # e.g. "1.09.12"
      "title": str,
      "text": str,        # raw Markdown of the section body
      "file": str,        # path relative to rules_dir
      "level": int,       # 1 = top-level file section, 2 = first subsection, …
      "parent": str|null,
      "children": [str],  # sorted
      "links_out": [str], # section IDs referenced from this section's text
      "links_in": [str],  # sections that reference this one (computed)
    }
  },
  "glossary": {
    "<term>": {
      "term": str,
      "definition": str,
      "sections": [str],  # section IDs listed for this term
    }
  },
  "index": {
    "<term>": [str],      # term → [section_id, …]  (derived from glossary)
  }
}
"""

import datetime
import json
import re
import sys
from pathlib import Path


### Constants ###


# Files skipped unconditionally (navigation-only READMEs with no anchored sections)
_NAV_FILENAMES = {"README.md"}

# Glossary file (parsed separately)
_GLOSSARY_FILE = "07-index-and-glossary.md"

# Extract title from header: strip leading #, section-number, and {#…}
_TITLE_STRIP_RE = re.compile(
    r"^#{1,6}\s+" r"[\d]+(?:\.[\d.]*)*" r"\.?\s*" r"(.*?)" r"\s*\{#[\d.]+\}" r"\s*$"
)

# Cross-references: markdown links with #section_id anchor
_MDREF_RE = re.compile(r"\[.*?\]\([^)]*#([\d.]+)\)")

# Bare section codes in running text, e.g. "(1.11.372 and 1.12.3)"
_BARE_RE = re.compile(r"(?<!\w)([\d]+\.[\d]+(?:\.[\d]+)*)(?!\w)")

# Navigation breadcrumb lines to strip
_NAV_LINE_RE = re.compile(r"^\s*\[←")

# Bold-term glossary entry opener (colon may be inside the ** markers: **Term:**)
_GLOSS_ENTRY_RE = re.compile(r"^\*\*([^*]+)\*\*:?\s*(.*)")

# Letter-section header inside glossary (### A, ## B, …)
_LETTER_HDR_RE = re.compile(r"^#{1,3}\s+[A-Z]$")


### Helpers ###


def _extract_title(header_line: str) -> str:
    m = _TITLE_STRIP_RE.match(header_line.strip())
    if m:
        return m.group(1).strip()
    # Fallback: remove anchors/hashes manually
    t = re.sub(r"^#{1,6}\s*", "", header_line)
    t = re.sub(r"\{#[\d.]+\}", "", t)
    t = re.sub(r"^[\d]+(?:\.[\d.]*)*\.?\s*", "", t)
    return t.strip()


def _extract_refs(text: str) -> list[str]:
    """Return all section IDs referenced in *text* (deduped, order-preserving)."""
    seen: dict[str, None] = {}
    for m in _MDREF_RE.finditer(text):
        seen[m.group(1)] = None
    for m in _BARE_RE.finditer(text):
        seen[m.group(1)] = None
    return list(seen)


def _compute_parent(section_id: str, all_ids: set[str]) -> str | None:
    """
    Infer parent by progressively stripping the rightmost digit of the last
    dot-segment.  Falls back to the prefix (one level up in the dot hierarchy).

    Examples
    --------
    1.09.12   → tries 1.09.1  → if found, returns it; else returns 1.09
    1.07.3321 → tries 1.07.332, 1.07.33, 1.07.3, 1.07
    1.09      → tries 1.0 … → falls back to "1"
    1         → None  (top-level)
    """
    parts = section_id.split(".")
    if len(parts) == 1:
        return None  # top-level

    last = parts[-1]
    prefix = ".".join(parts[:-1])

    # Try shorter versions of the last segment first
    for i in range(len(last) - 1, 0, -1):
        candidate = f"{prefix}.{last[:i]}"
        if candidate in all_ids:
            return candidate

    # Fall back to the prefix itself
    if prefix in all_ids:
        return prefix

    # Prefix not in DB — recurse upward (handles missing intermediate levels)
    if "." in prefix:
        return _compute_parent(prefix, all_ids)

    return None  # single-segment prefix that doesn't exist in DB


### File parser ###


def _parse_sections_from_file(filepath: Path, rules_dir: Path) -> list[dict]:
    """Return a list of section dicts extracted from one Markdown file."""
    try:
        text = filepath.read_text(encoding="utf-8")
    except OSError as e:
        print(f"  Warning: could not read {filepath}: {e}", file=sys.stderr)
        return []

    rel_path = filepath.relative_to(rules_dir).as_posix()
    lines = text.splitlines()

    sections: list[dict] = []
    cur_id: str | None = None
    cur_title: str = ""
    cur_lines: list[str] = []

    def _flush():
        nonlocal cur_id, cur_title, cur_lines
        if cur_id is None:
            return
        sections.append(
            {
                "id": cur_id,
                "title": cur_title,
                "text": "\n".join(cur_lines).strip(),
                "file": rel_path,
                "level": cur_id.count(".") + 1,
                "parent": None,
                "children": [],
                "links_out": [],
                "links_in": [],
            }
        )
        cur_id = None
        cur_title = ""
        cur_lines = []

    for line in lines:
        # Detect header with anchor
        if line.lstrip().startswith("#") and "{#" in line:
            m = re.search(r"\{#([\d.]+)\}", line)
            if m:
                _flush()
                cur_id = m.group(1)
                cur_title = _extract_title(line)
                cur_lines = []
                continue

        # Skip nav breadcrumb lines
        if _NAV_LINE_RE.match(line):
            continue

        if cur_id is not None:
            cur_lines.append(line)

    _flush()
    return sections


### Glossary parser ###


def _parse_glossary(filepath: Path) -> tuple[dict, dict]:
    """
    Parse the index/glossary file.

    Returns (glossary, index):
        glossary: term → {term, definition, sections}
        index:    term → [section_id, …]
    """
    try:
        raw = filepath.read_text(encoding="utf-8")
    except OSError as e:
        print(f"  Warning: could not read glossary {filepath}: {e}", file=sys.stderr)
        return {}, {}

    # Split text before each bold-term entry so each chunk starts with **Term:**
    chunks = re.split(r"\n(?=\*\*[^*]+\*\*)", raw)

    glossary: dict = {}
    index: dict = {}

    for chunk in chunks:
        m = _GLOSS_ENTRY_RE.match(chunk.strip())
        if not m:
            continue

        term = m.group(1).strip().rstrip(":")
        # Collect full content (rest of first line + continuation lines)
        content_lines = [m.group(2)]
        for line in chunk.splitlines()[1:]:
            stripped = line.strip()
            if _LETTER_HDR_RE.match(stripped) or stripped.startswith("#"):
                break
            content_lines.append(stripped)
        content = " ".join(content_lines)

        # Extract section refs (markdown links take priority, then bare codes)
        refs = _extract_refs(content)

        # Build human-readable definition: remove markdown links and
        # parenthetical reference blocks like ([1.09.12](...))
        defn = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", content)
        defn = re.sub(r"\(\s*[^)]*\)\s*", " ", defn)
        defn = re.sub(r"\s+", " ", defn).strip().rstrip(".")

        glossary[term] = {
            "term": term,
            "definition": defn,
            "sections": refs,
        }
        if refs:
            index[term] = refs

    return glossary, index


### Main build function ###


def build_database(
    rules_dir: Path,
    output_path: Path,
    json_mode: bool,
) -> None:
    rules_dir = Path(rules_dir).resolve()
    output_path = Path(output_path).resolve()

    if not rules_dir.exists():
        msg = f"Rules directory not found: {rules_dir}"
        if json_mode:
            print(json.dumps({"error": msg}))
        else:
            print(f"Error: {msg}", file=sys.stderr)
        sys.exit(1)

    if not json_mode:
        print(f"Building rorcli database from: {rules_dir}")

    all_sections: dict[str, dict] = {}
    glossary: dict = {}
    index: dict = {}

    for filepath in sorted(rules_dir.rglob("*.md")):
        filename = filepath.name

        # Always skip navigation READMEs
        if filename in _NAV_FILENAMES:
            continue

        # Handle glossary file separately
        if filename == _GLOSSARY_FILE:
            glossary, index = _parse_glossary(filepath)
            if not json_mode:
                print(f"  Parsed glossary: {len(glossary)} terms")
            continue

        sections = _parse_sections_from_file(filepath, rules_dir)
        for s in sections:
            all_sections[s["id"]] = s
        if not json_mode and sections:
            print(
                f"  {filepath.relative_to(rules_dir).as_posix()}: {len(sections)} sections"
            )

    # parent/child relationships
    all_ids = set(all_sections)
    for sid, section in all_sections.items():
        parent = _compute_parent(sid, all_ids)
        section["parent"] = parent
        if parent and parent in all_sections:
            all_sections[parent]["children"].append(sid)

    for section in all_sections.values():
        section["children"].sort()

    # cross-references (links_out / links_in)
    for sid, section in all_sections.items():
        raw_refs = _extract_refs(section.get("text", ""))
        section["links_out"] = [r for r in raw_refs if r in all_ids and r != sid]

        for ref in section["links_out"]:
            if sid not in all_sections[ref]["links_in"]:
                all_sections[ref]["links_in"].append(sid)

    # write output
    output_path.parent.mkdir(parents=True, exist_ok=True)

    db = {
        "meta": {
            "built_at": datetime.datetime.utcnow().isoformat() + "Z",
            "rules_dir": str(rules_dir),
            "total_sections": len(all_sections),
            "total_glossary_terms": len(glossary),
        },
        "sections": all_sections,
        "glossary": glossary,
        "index": index,
    }

    output_path.write_text(
        json.dumps(db, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    if json_mode:
        print(
            json.dumps(
                {
                    "status": "ok",
                    "output": str(output_path),
                    "sections": len(all_sections),
                    "glossary_terms": len(glossary),
                    "index_entries": len(index),
                }
            )
        )
    else:
        print(f"\nDone.")
        print(f"  Sections:       {len(all_sections)}")
        print(f"  Glossary terms: {len(glossary)}")
        print(f"  Index entries:  {len(index)}")
        print(f"  Output:         {output_path}")
