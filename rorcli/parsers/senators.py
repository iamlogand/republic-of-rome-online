import sys
from pathlib import Path

from rorcli.parsers.tables import parse_markdown_table


def parse_senators(filepath: Path) -> dict:
    """Parse senators.md → dict keyed by senator number string."""
    try:
        text = filepath.read_text(encoding="utf-8")
    except OSError as e:
        print(f"  Warning: could not read {filepath}: {e}", file=sys.stderr)
        return {}

    pipe_lines = [l for l in text.splitlines() if l.strip().startswith("|")]
    rows = parse_markdown_table(pipe_lines)

    senators: dict = {}
    for row in rows:
        num = row.get("#", "").strip()
        if not num.isdigit():
            continue
        senators[num] = {
            "name": row["name"],
            "era": row["era"].lower(),
            "m": int(row["military"]),
            "o": int(row["oratory"]),
            "l": int(row["loyalty"]),
            "i": int(row["influence"]),
        }

    return senators
