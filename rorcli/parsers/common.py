import sys
from pathlib import Path


def read_text(filepath: Path) -> str | None:
    try:
        return filepath.read_text(encoding="utf-8")
    except OSError as e:
        print(f"  Warning: could not read {filepath}: {e}", file=sys.stderr)
        return None


def collect_bullets(lines: list[str]) -> list[str]:
    return [ln.strip()[2:].strip() for ln in lines if ln.strip().startswith("- ")]


def int_or_none(s: str, *, strip_plus: bool = False) -> int | None:
    s = s.strip()
    if strip_plus:
        s = s.lstrip("+")
    if s in ("—", "-", ""):
        return None
    try:
        return int(s)
    except ValueError:
        return None


def extract_meta_table_lines(lines: list[str], anchor_prefix: str) -> list[str]:
    in_meta = False
    pipe_lines: list[str] = []
    for line in lines:
        if f"{{#{anchor_prefix}-meta}}" in line:
            in_meta = True
            continue
        if in_meta:
            if line.startswith("##"):
                break
            if line.strip().startswith("|"):
                pipe_lines.append(line)
    return pipe_lines
