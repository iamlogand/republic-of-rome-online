import re
from pathlib import Path
from typing import Optional

from .common import read_text


_NAV_FILENAMES = {"README.md"}
_GLOSSARY_FILENAME = "07-index-and-glossary.md"

_TITLE_STRIP_RE = re.compile(
    r"^#{1,6}\s+" r"[\d]+(?:\.[\d.]*)*" r"\.?\s*" r"(.*?)" r"\s*\{#[\d.]+\}" r"\s*$"
)
_ANCHOR_RE = re.compile(r"\{#([A-Za-z0-9][A-Za-z0-9._-]*)\}")
_COMP_TITLE_STRIP_RE = re.compile(
    r"^#{1,6}\s+(.*?)\s*\{#[A-Za-z0-9][A-Za-z0-9._-]*\}\s*$"
)
_MD_REF_RE = re.compile(r"\[.*?\]\([^)]*#([\d.]+)\)")
_MD_LINK_RE = re.compile(r"\[([^\]\[()]+)\]\(([^)]+)\)")
_ANCHOR_CODE_RE = re.compile(r"#([\d.]+)$")
_BARE_RE = re.compile(r"(?<!\w)([\d]+\.[\d]+(?:\.[\d]+)*)(?!\w)")
_NAV_LINE_RE = re.compile(r"^\s*\[←")
_GLOSSARY_ENTRY_RE = re.compile(r"^\*\*([^*]+)\*\*:?\s*(.*)")
_LETTER_HDR_RE = re.compile(r"^#{1,3}\s+[A-Z]$")
_GLOSSARY_SPLIT_RE = re.compile(r"\n(?=\*\*[^*]+\*\*)")
_GLOSSARY_LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")
_GLOSSARY_PARENS_RE = re.compile(r"\(\s*[^)]*\)\s*")
_GLOSSARY_WS_RE = re.compile(r"\s+")


def _strip_md_links(text: str) -> str:
    text = text.replace("\\[", "\x00LBKT\x00").replace("\\]", "\x00RBKT\x00")

    def _repl(match: re.Match[str]) -> str:
        label, target = match.group(1), match.group(2)
        anchor = _ANCHOR_CODE_RE.search(target)
        if anchor:
            sec = anchor.group(1)
            return f"[§{sec}]" if label.strip() == sec else f"{label} [§{sec}]"
        return label

    text = _MD_LINK_RE.sub(_repl, text)
    return text.replace("\x00LBKT\x00", "[").replace("\x00RBKT\x00", "]")


def _extract_title(header_line: str) -> str:
    match = _TITLE_STRIP_RE.match(header_line.strip())
    if match:
        return match.group(1).strip()
    match = _COMP_TITLE_STRIP_RE.match(header_line.strip())
    if match:
        return match.group(1).strip()
    return header_line.strip()


def _extract_refs(text: str) -> list[str]:
    seen: dict[str, None] = {}
    for match in _MD_REF_RE.finditer(text):
        seen[match.group(1)] = None
    for match in _BARE_RE.finditer(text):
        seen[match.group(1)] = None
    return list(seen)


def _compute_parent(section_id: str, all_ids: set[str]) -> Optional[str]:
    parts = section_id.split(".")
    if len(parts) == 1:
        return None

    last = parts[-1]
    prefix = ".".join(parts[:-1])

    for i in range(len(last) - 1, 0, -1):
        candidate = f"{prefix}.{last[:i]}"
        if candidate in all_ids:
            return candidate

    if prefix in all_ids:
        return prefix

    if "." in prefix:
        return _compute_parent(prefix, all_ids)

    return None


def parse_rulebook(rules_dir: Path) -> tuple[dict, dict]:
    rules: dict[str, dict] = {}
    glossary: dict = {}

    for filepath in sorted(rules_dir.rglob("*.md")):
        filename = filepath.name
        if filename in _NAV_FILENAMES:
            continue
        if filename == _GLOSSARY_FILENAME:
            glossary = parse_glossary(filepath)
            continue
        for rule in parse_rules(filepath):
            rules[rule["id"]] = rule

    all_ids = set(rules)
    for id, rule in rules.items():
        parent = _compute_parent(id, all_ids)
        rule["parent"] = parent
        if parent and parent in rules:
            rules[parent]["children"].append(id)

    for rule in rules.values():
        rule["children"].sort()

    for id, rule in rules.items():
        parent_id = rule["parent"]
        if parent_id and parent_id in rules:
            siblings = rules[parent_id]["children"]
            idx = siblings.index(id)
            rule["prev"] = siblings[idx - 1] if idx > 0 else None
            rule["next"] = siblings[idx + 1] if idx < len(siblings) - 1 else None
        else:
            rule["prev"] = None
            rule["next"] = None

    for id, rule in rules.items():
        raw_refs = _extract_refs(rule.get("text", ""))
        rule["links_out"] = [r for r in raw_refs if r in all_ids and r != id]
        rule["text"] = _strip_md_links(rule.get("text", ""))
        for ref in rule["links_out"]:
            if id not in rules[ref]["links_in"]:
                rules[ref]["links_in"].append(id)

    return rules, glossary


def parse_rules(filepath: Path) -> list[dict]:
    text = read_text(filepath)
    if text is None:
        return []

    lines = text.splitlines()

    rules: list[dict] = []
    current_id: Optional[str] = None
    current_title: str = ""
    current_lines: list[str] = []

    def _flush():
        nonlocal current_id, current_title, current_lines
        if current_id is None:
            return
        rules.append(
            {
                "id": current_id,
                "title": current_title,
                "text": "\n".join(current_lines).strip(),
                "level": current_id.count(".") + 1,
                "parent": None,
                "children": [],
                "prev": None,
                "next": None,
                "links_out": [],
                "links_in": [],
            }
        )
        current_id = None
        current_title = ""
        current_lines = []

    for line in lines:
        if line.lstrip().startswith("#") and "{#" in line:
            match = _ANCHOR_RE.search(line)
            if match:
                _flush()
                current_id = match.group(1)
                current_title = _extract_title(line)
                current_lines = []
                continue

        if _NAV_LINE_RE.match(line):
            continue

        if current_id is not None:
            current_lines.append(line)

    _flush()
    return rules


def parse_glossary(filepath: Path) -> dict:
    raw = read_text(filepath)
    if raw is None:
        return {}

    chunks = _GLOSSARY_SPLIT_RE.split(raw)

    glossary: dict = {}

    for chunk in chunks:
        match = _GLOSSARY_ENTRY_RE.match(chunk.strip())
        if not match:
            continue

        term = match.group(1).strip().rstrip(":")
        content_lines = [match.group(2)]
        for line in chunk.splitlines()[1:]:
            stripped = line.strip()
            if _LETTER_HDR_RE.match(stripped) or stripped.startswith("#"):
                break
            content_lines.append(stripped)
        content = " ".join(content_lines)

        refs = _extract_refs(content)

        definition = _GLOSSARY_LINK_RE.sub(r"\1", content)
        definition = _GLOSSARY_PARENS_RE.sub(" ", definition)
        definition = _GLOSSARY_WS_RE.sub(" ", definition).strip().strip(".,; ").strip()

        glossary[term] = {
            "definition": definition,
            "rule_ids": refs,
        }

    return glossary
