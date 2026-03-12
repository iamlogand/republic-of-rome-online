import re


def _is_separator(line: str) -> bool:
    """True if the line is a table separator row (| --- | :---: | etc.)."""
    stripped = line.strip()
    if not stripped.startswith("|"):
        return False
    return all(
        re.fullmatch(r":?-+:?", cell.strip())
        for cell in stripped.strip("|").split("|")
        if cell.strip()
    )


def _split_cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def parse_markdown_table(lines: list[str]) -> list[dict]:
    """Parse a sequence of lines forming one Markdown table → list of row dicts.

    - First non-separator pipe row is treated as the header.
    - Separator rows are skipped.
    - Data rows are zipped against the header; extra cells are discarded, missing cells are filled with empty string.
    - Returns an empty list if no header row is found.
    """
    header: list[str] = []
    rows: list[dict] = []

    for line in lines:
        if not line.strip().startswith("|"):
            continue
        if _is_separator(line):
            continue
        cells = _split_cells(line)
        if not header:
            header = [c.lower().replace(" ", "_") for c in cells]
            continue
        n = len(header)
        padded = (cells + [""] * n)[:n]
        rows.append(dict(zip(header, padded)))

    return rows
