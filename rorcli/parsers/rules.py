import re
import sys
from pathlib import Path


### Constants ###


# Files skipped unconditionally (navigation-only READMEs with no anchored sections)
NAV_FILENAMES = {"README.md"}

# Glossary file (parsed separately)
GLOSSARY_FILE = "07-index-and-glossary.md"

# Extract title from header: strip leading #, section-number, and {#…}
_TITLE_STRIP_RE = re.compile(
    r"^#{1,6}\s+" r"[\d]+(?:\.[\d.]*)*" r"\.?\s*" r"(.*?)" r"\s*\{#[\d.]+\}" r"\s*$"
)

# Matches both numeric {#1.09.12} and hyphenated {#senator-early} anchors
_ANCHOR_RE = re.compile(r"\{#([A-Za-z0-9][A-Za-z0-9._-]*)\}")

# For component-style headers: "#### 1A — Scipio Africanus {#statesman-1a}"
_COMP_TITLE_STRIP_RE = re.compile(
    r"^#{1,6}\s+(.*?)\s*\{#[A-Za-z0-9][A-Za-z0-9._-]*\}\s*$"
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

# Glossary helpers — used in _parse_glossary
# Split raw text before each bold-term entry
_GLOSS_SPLIT_RE = re.compile(r"\n(?=\*\*[^*]+\*\*)")
# Replace markdown links with their display text
_GLOSS_LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")
# Strip parenthetical reference blocks (e.g. "(see 1.09.12)")
_GLOSS_PARENS_RE = re.compile(r"\(\s*[^)]*\)\s*")
# Collapse runs of whitespace
_GLOSS_WS_RE = re.compile(r"\s+")


### Helpers ###


def _extract_title(header_line: str) -> str:
    m = _TITLE_STRIP_RE.match(header_line.strip())
    if m:
        return m.group(1).strip()
    m = _COMP_TITLE_STRIP_RE.match(header_line.strip())
    if m:
        return m.group(1).strip()
    return header_line.strip()


def extract_refs(text: str) -> list[str]:
    """Return all section IDs referenced in *text* (deduped, order-preserving)."""
    seen: dict[str, None] = {}
    for m in _MDREF_RE.finditer(text):
        seen[m.group(1)] = None
    for m in _BARE_RE.finditer(text):
        seen[m.group(1)] = None
    return list(seen)


def compute_parent(section_id: str, all_ids: set[str]) -> str | None:
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
        return compute_parent(prefix, all_ids)

    return None  # single-segment prefix that doesn't exist in DB


### File parser ###


def parse_sections_from_file(filepath: Path, rules_dir: Path) -> list[dict]:
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
            m = _ANCHOR_RE.search(line)
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


def parse_glossary(filepath: Path) -> tuple[dict, dict]:
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
    chunks = _GLOSS_SPLIT_RE.split(raw)

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
        refs = extract_refs(content)

        # Build human-readable definition: remove markdown links and
        # parenthetical reference blocks like ([1.09.12](...))
        defn = _GLOSS_LINK_RE.sub(r"\1", content)
        defn = _GLOSS_PARENS_RE.sub(" ", defn)
        defn = _GLOSS_WS_RE.sub(" ", defn).strip().rstrip(".")

        glossary[term] = {
            "term": term,
            "definition": defn,
            "sections": refs,
        }
        if refs:
            index[term] = refs

    return glossary, index
