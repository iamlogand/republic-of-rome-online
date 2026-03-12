import re
import sys
from pathlib import Path

from .tables import parse_markdown_table

# Markdown link in statesman table cell: "[1A — Name](#statesman-slug)"
_STATESMAN_CELL_RE = re.compile(
    r"\[(\d+[A-Za-z]+)\s+[—-]\s+([^\]]+)\]\(#statesman-([A-Za-z0-9-]+)\)"
)
# Extracts the family senator number from a family column value: "Cornelius (#1)" → 1
_FAMILY_NUM_RE = re.compile(r"#(\d+)")
# Individual statesman section headers: "## Code — Name {#statesman-slug}"
_SECTION_HDR_RE = re.compile(r"^##\s+.*\{#statesman-([A-Za-z0-9-]+)\}")
# Special ability bullet (optional — some sections use plain bullets instead)
_SPECIAL_RE = re.compile(r"^-\s+Special:\s*(.+)")


def _int_or_val(s: str) -> int | str | None:
    """Return int if parseable, the raw string if not, None if blank/dash."""
    s = s.strip()
    if s in ("—", "-", ""):
        return None
    try:
        return int(s)
    except ValueError:
        return s


def parse_statesmen(filepath: Path) -> dict:
    """Parse statesmen.md → dict keyed by slug (e.g. '1a')."""
    try:
        text = filepath.read_text(encoding="utf-8")
    except OSError as e:
        print(f"  Warning: could not read {filepath}: {e}", file=sys.stderr)
        return {}

    statesmen: dict = {}
    lines = text.splitlines()

    # --- Pass 1: summary table ---
    # Columns: Statesman | Deck | Family | MIL | ORA | LOY | Conflicts | INF | POP
    in_meta = False
    pipe_lines: list[str] = []
    for line in lines:
        if "{#statesman-meta}" in line:
            in_meta = True
            continue
        if in_meta:
            if line.startswith("##"):
                break
            if line.strip().startswith("|"):
                pipe_lines.append(line)

    for row in parse_markdown_table(pipe_lines):
        m = _STATESMAN_CELL_RE.search(row["statesman"])
        if not m:
            continue
        code = m.group(1)
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
            "code": code,
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

    # --- Pass 2: individual section notes/special abilities ---
    # Sections with "- Special: ..." store that as `special`.
    # Sections with plain bullets (no Special: prefix) store them as `notes`.
    current_slug: str | None = None
    current_lines: list[str] = []

    def _flush() -> None:
        nonlocal current_slug, current_lines
        if current_slug and current_slug in statesmen:
            bullets = [
                ln.strip()[2:].strip()
                for ln in current_lines
                if ln.strip().startswith("- ") and ln.strip()[2:].strip()
            ]
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
            slug = m.group(1)  # e.g. "1a", or "meta" for the table section
            current_slug = slug if slug in statesmen else None
            continue
        if current_slug is not None:
            current_lines.append(line)

    _flush()
    return statesmen
