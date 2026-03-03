"""
Query layer: reads rorcli.db.json and implements the CLI commands.
"""

import json
import sys
import textwrap
from pathlib import Path
from typing import Any, cast


### DB loading ###


def load_db(db_path: Path) -> dict[str, Any]:
    """Load and return the rorcli database."""
    db_path = Path(db_path)
    if not db_path.exists():
        print(
            f"Error: Database not found at {db_path}\n" f"Run 'rorcli build' first.",
            file=sys.stderr,
        )
        sys.exit(1)

    return cast(dict[str, Any], json.loads(db_path.read_text(encoding="utf-8")))


### Output helpers ###


def _clean_md(text: str) -> str:
    """Strip Markdown link syntax for human display, keeping section codes visible.

    [text](path#1.09.12)  →  text [§1.09.12]
    [1.09.12](path)       →  [§1.09.12]
    \\[EXCEPTION: …\\]    →  [EXCEPTION: …]
    """
    import re as _re

    # Replace escaped brackets first so they don't confuse the link regex.
    text = text.replace("\\[", "\x00LBKT\x00").replace("\\]", "\x00RBKT\x00")

    # Markdown links: label must not contain [ ] ( ) to avoid greedy over-match
    def _repl(m: "_re.Match[str]") -> str:
        label, target = m.group(1), m.group(2)
        anchor = _re.search(r"#([\d.]+)$", target)
        if anchor:
            sec = anchor.group(1)
            if label.strip() == sec:
                return f"[§{sec}]"
            return f"{label} [§{sec}]"
        return label

    text = _re.sub(r"\[([^\]\[()]+)\]\(([^)]+)\)", _repl, text)

    # Restore escaped brackets
    text = text.replace("\x00LBKT\x00", "[").replace("\x00RBKT\x00", "]")
    return text


def _wrap(text: str, width: int = 88, indent: str = "") -> str:
    """Clean markdown and re-wrap text, preserving paragraph breaks."""
    text = _clean_md(text)
    paragraphs = text.split("\n\n")
    wrapped = []
    for para in paragraphs:
        lines = para.splitlines()
        # Preserve lines that look like list items or block-quotes
        if lines and lines[0].lstrip().startswith(("-", "*", ">", "#")):
            wrapped.append(para)
        else:
            collapsed = " ".join(ln.strip() for ln in lines if ln.strip())
            if collapsed:
                wrapped.append(
                    textwrap.fill(
                        collapsed,
                        width=width,
                        initial_indent=indent,
                        subsequent_indent=indent,
                    )
                )
    return "\n\n".join(wrapped)


def _divider(char: str = "─", width: int = 70) -> str:
    return char * width


def _section_header(section: dict) -> str:
    return f"[{section['id']}]  {section['title']}"


def _error(msg: str, json_mode: bool) -> None:
    if json_mode:
        print(json.dumps({"error": msg}))
    else:
        print(f"Error: {msg}", file=sys.stderr)


### Commands ###


def cmd_show(db: dict, section_code: str, *, json_mode: bool) -> None:
    """rorcli show <section_code> — display the full text of one section."""
    section = db["sections"].get(section_code)
    if section is None:
        _error(f"Section {section_code!r} not found.", json_mode)
        return

    if json_mode:
        print(json.dumps(section, indent=2, ensure_ascii=False))
        return

    print()
    print(_divider("═"))
    print(_section_header(section))
    print(_divider("─"))
    print(f"File  : {section['file']}")
    if section["parent"]:
        parent = db["sections"].get(section["parent"])
        plabel = (
            f"[{section['parent']}] {parent['title']}" if parent else section["parent"]
        )
        print(f"Parent: {plabel}")
    if section["children"]:
        kids = section["children"]
        suffix = " …" if len(kids) > 12 else ""
        print(f"Sub-sections ({len(kids)}): {', '.join(kids[:12])}{suffix}")
    print(_divider("─"))
    print()
    print(_wrap(section["text"]))
    if section["links_out"]:
        refs = section["links_out"][:8]
        suffix = " …" if len(section["links_out"]) > 8 else ""
        print(f"\nSee also: {', '.join(f'[{r}]' for r in refs)}{suffix}")
    print()


def cmd_search(db: dict, term: str, *, json_mode: bool) -> None:
    """rorcli search <term> — full-text search across sections and glossary."""
    term_lower = term.lower()
    results: list[dict] = []

    # 1. Glossary matches
    for t, entry in db["glossary"].items():
        if term_lower in t.lower():
            results.append(
                {
                    "type": "glossary",
                    "term": t,
                    "definition": entry["definition"],
                    "sections": entry["sections"],
                }
            )

    # 2. Section title / text matches
    section_hits: list[tuple[int, dict]] = []
    for sid, section in db["sections"].items():
        score = 0
        if term_lower in section["title"].lower():
            score += 10
        text_lower = section.get("text", "").lower()
        if term_lower in text_lower:
            score += max(1, min(5, text_lower.count(term_lower)))
        if score:
            section_hits.append((score, section))

    section_hits.sort(key=lambda p: p[0], reverse=True)

    for score, section in section_hits[:15]:
        results.append(
            {
                "type": "section",
                "id": section["id"],
                "title": section["title"],
                "file": section["file"],
                "score": score,
            }
        )

    if json_mode:
        print(
            json.dumps({"term": term, "results": results}, indent=2, ensure_ascii=False)
        )
        return

    if not results:
        print(f"No results for {term!r}.")
        return

    print()
    print(
        f"Search results for {term!r}  ({len(results)} match{'es' if len(results) != 1 else ''})"
    )
    print(_divider())

    for r in results:
        if r["type"] == "glossary":
            defn_short = r["definition"][:120] + (
                "…" if len(r["definition"]) > 120 else ""
            )
            print(f"\n[GLOSSARY]  {r['term']}")
            print(f"  {defn_short}")
            if r["sections"]:
                suffix = " …" if len(r["sections"]) > 6 else ""
                print(f"  Sections: {', '.join(r['sections'][:6])}{suffix}")
        else:
            print(f"\n[{r['id']}]  {r['title']}  (score {r['score']})")
            print(f"  {r['file']}")
    print()


def cmd_explain(db: dict, term: str, *, json_mode: bool) -> None:
    """rorcli explain <term> — full glossary entry + text of each referenced section."""
    # Case-insensitive exact match first, then partial
    entry = None
    term_lower = term.lower()
    for t, e in db["glossary"].items():
        if t.lower() == term_lower:
            entry = e
            break
    if entry is None:
        for t, e in db["glossary"].items():
            if term_lower in t.lower():
                entry = e
                break

    if entry is None:
        _error(
            f"Term {term!r} not found in glossary.  Try: rorcli search {term}",
            json_mode,
        )
        return

    related = [
        db["sections"][sid] for sid in entry["sections"] if sid in db["sections"]
    ]

    if json_mode:
        print(
            json.dumps(
                {**entry, "related_sections": related}, indent=2, ensure_ascii=False
            )
        )
        return

    print()
    print(_divider("═"))
    print(f"TERM:  {entry['term']}")
    print(_divider("─"))
    print(_wrap(entry["definition"]))
    if entry["sections"]:
        print(f"\nSection references: {', '.join(entry['sections'])}")

    for section in related:
        print()
        print(_divider("·"))
        print(f"  [{section['id']}]  {section['title']}")
        print(_divider("·"))
        body = section.get("text", "").strip()
        if not body:
            children = section.get("children", [])
            if children:
                child_labels = ", ".join(f"[{c}]" for c in children[:6])
                suffix = " …" if len(children) > 6 else ""
                print(
                    f"  (container section — see sub-sections: {child_labels}{suffix})"
                )
            else:
                print("  (no text)")
        else:
            preview = body[:600]
            if len(body) > 600:
                preview += "\n  …"
            print(_wrap(preview, indent="  "))

    print()


def cmd_context(db: dict, section_code: str, *, json_mode: bool) -> None:
    """rorcli context <section_code> — section with parent, siblings, children, and links."""
    section = db["sections"].get(section_code)
    if section is None:
        _error(f"Section {section_code!r} not found.", json_mode)
        return

    parent = db["sections"].get(section["parent"]) if section["parent"] else None

    siblings = [
        db["sections"][sid]
        for sid in (parent["children"] if parent else [])
        if sid != section_code and sid in db["sections"]
    ]
    children = [
        db["sections"][sid] for sid in section["children"] if sid in db["sections"]
    ]
    links_out = [
        db["sections"][r] for r in section["links_out"] if r in db["sections"]
    ][:8]
    links_in = [db["sections"][r] for r in section["links_in"] if r in db["sections"]][
        :8
    ]

    if json_mode:
        print(
            json.dumps(
                {
                    "section": section,
                    "parent": parent,
                    "siblings": siblings,
                    "children": children,
                    "links_out": links_out,
                    "links_in": links_in,
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return

    print()
    print(_divider("═"))
    print(_section_header(section))
    print(_divider("═"))

    # Ancestry breadcrumb
    crumb: list[str] = []
    if parent:
        crumb.append(f"[{parent['id']}] {parent['title']}")
    crumb.append(f"[{section['id']}] {section['title']}  ◄")
    if children:
        crumb.append(f"({len(children)} sub-sections)")
    print("  →  ".join(crumb))

    # Siblings
    if siblings and parent is not None:
        print()
        print(f"SIBLINGS  ({len(siblings)} others under [{parent['id']}])")
        for s in siblings[:8]:
            print(f"    [{s['id']}] {s['title']}")
        if len(siblings) > 8:
            print(f"    … and {len(siblings) - 8} more")

    # Section text
    print()
    print(_divider("─"))
    print(_wrap(section["text"]))
    print(_divider("─"))

    # Children
    if children:
        print(f"\nSUB-SECTIONS  ({len(children)})")
        for c in children:
            preview = c.get("text", "").replace("\n", " ")[:80]
            if len(c.get("text", "")) > 80:
                preview += "…"
            print(f"  [{c['id']}]  {c['title']}")
            if preview:
                print(f"       {preview}")

    # Cross-links
    if links_out:
        print(f"\nREFERENCES OUT  ({len(section['links_out'])})")
        for s in links_out:
            print(f"  [{s['id']}]  {s['title']}")
        if len(section["links_out"]) > 8:
            print(f"  … and {len(section['links_out']) - 8} more")

    if links_in:
        print(f"\nREFERENCED BY  ({len(section['links_in'])})")
        for s in links_in:
            print(f"  [{s['id']}]  {s['title']}")
        if len(section["links_in"]) > 8:
            print(f"  … and {len(section['links_in']) - 8} more")

    print()
