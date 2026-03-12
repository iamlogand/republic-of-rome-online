"""
Query layer: reads rorcli.db.json and implements the CLI commands.
"""

import json
import re
import sys
import textwrap
from pathlib import Path
from typing import Any, cast

# Matches a Markdown inline link: [label](target) — label must not contain []()
_MD_LINK_RE = re.compile(r"\[([^\]\[()]+)\]\(([^)]+)\)")
# Extracts a section code from the end of a link target: #1.09.12
_ANCHOR_CODE_RE = re.compile(r"#([\d.]+)$")

# Maps section ID prefix → components dict key for structured component data lookup
_COMPONENT_PREFIXES: dict[str, str] = {
    "war": "wars",
    "leader": "leaders",
    "province": "provinces",
    "law": "laws",
    "event": "events",
    "intrigue": "intrigue",
    "concession": "concessions",
    "senator": "senators",
    "statesman": "statesmen",
    "board": "board",
}
# Reverse mapping: components dict key → section ID prefix
_COMP_TYPE_TO_PREFIX: dict[str, str] = {v: k for k, v in _COMPONENT_PREFIXES.items()}


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
    # Replace escaped brackets first so they don't confuse the link regex.
    text = text.replace("\\[", "\x00LBKT\x00").replace("\\]", "\x00RBKT\x00")

    # Markdown links: label must not contain [ ] ( ) to avoid greedy over-match
    def _repl(m: re.Match[str]) -> str:
        label, target = m.group(1), m.group(2)
        anchor = _ANCHOR_CODE_RE.search(target)
        if anchor:
            sec = anchor.group(1)
            if label.strip() == sec:
                return f"[§{sec}]"
            return f"{label} [§{sec}]"
        return label

    text = _MD_LINK_RE.sub(_repl, text)

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


### Component lookup ###


def _lookup_component(db: dict, section_id: str) -> tuple[str, dict] | tuple[None, None]:
    """Return (comp_type, component_dict) for a section ID that maps to a component."""
    components = db.get("components", {})
    for prefix, comp_type in _COMPONENT_PREFIXES.items():
        if section_id.startswith(prefix + "-"):
            slug = section_id[len(prefix) + 1:]
            component = components.get(comp_type, {}).get(slug)
            if component is not None:
                return comp_type, component
    # misc components have heterogeneous anchors (bequest-*, catiline-*, etc.)
    component = components.get("misc", {}).get(section_id)
    if component is not None:
        return "misc", component
    return None, None


def _format_component(component: dict) -> str:
    """Render structured component fields as human-readable lines.

    Skips fields already visible in the section text (name, notes, description, text).
    Nested dicts (e.g. province undeveloped/developed) are rendered as sub-blocks.
    """
    skip = {"name", "notes", "description", "text", "title"}
    lines: list[str] = []
    for key, value in component.items():
        if key in skip or value is None:
            continue
        label = key.replace("_", " ").title()
        if isinstance(value, dict):
            lines.append(f"{label}:")
            for k2, v2 in value.items():
                if v2 is None:
                    continue
                l2 = k2.replace("_", " ").title()
                lines.append(f"  {l2}: {v2}")
        elif isinstance(value, list):
            lines.append(f"{label}: {', '.join(str(v) for v in value)}")
        elif isinstance(value, bool):
            if value:
                lines.append(label)
        else:
            lines.append(f"{label}: {value}")
    return "\n".join(lines)


def _component_display_name(component: dict) -> str:
    """Human-readable title for a component."""
    name = component.get("name", "?")
    if "code" in component:
        return f"{component['code']} — {name}"
    return name


def _component_body(component: dict) -> str:
    """Displayable text fields from a component (description, notes, special, etc.)."""
    parts: list[str] = []
    if "description" in component and component["description"]:
        parts.append(component["description"])
    if "text" in component and component["text"]:
        parts.append(component["text"])
    if "special" in component and component["special"]:
        parts.append(f"Special: {component['special']}")
    if "notes" in component:
        for note in component["notes"]:
            parts.append(f"- {note}")
    return "\n".join(parts)


def _component_search_text(component: dict) -> str:
    """Concatenated searchable text for a component."""
    fields = ["name", "description", "text", "special", "effect"]
    parts = [str(component[f]) for f in fields if component.get(f)]
    if "notes" in component:
        parts.extend(component["notes"])
    return " ".join(parts)


def _component_id(comp_type: str, slug: str) -> str:
    """Reconstruct the section-style ID for a component."""
    prefix = _COMP_TYPE_TO_PREFIX.get(comp_type)
    return f"{prefix}-{slug}" if prefix else slug


### Commands ###


def cmd_show(db: dict, section_code: str, *, json_mode: bool) -> None:
    """rorcli show <section_code> — display a rules section or component."""
    section = db["rules"].get(section_code)
    comp_type, component = _lookup_component(db, section_code)

    if section is None and component is None:
        _error(f"{section_code!r} not found.", json_mode)
        sys.exit(1)

    # --- Component (not a rules section) ---
    if section is None:
        if json_mode:
            print(json.dumps({"id": section_code, "component": component}, indent=2, ensure_ascii=False))
            return
        print()
        print(_divider("═"))
        print(f"[{section_code}]  {_component_display_name(component)}")
        print(_divider("─"))
        component_text = _format_component(component)
        if component_text:
            print(component_text)
            print(_divider("·"))
        body = _component_body(component)
        if body:
            print()
            print(_wrap(body))
        print()
        return

    # --- Rules section (may also have associated component data) ---
    if json_mode:
        output = dict(section)
        if component is not None:
            output["component"] = component
        print(json.dumps(output, indent=2, ensure_ascii=False))
        return

    print()
    print(_divider("═"))
    print(_section_header(section))
    print(_divider("─"))
    print(f"File  : {section['file']}")
    if section["parent"]:
        parent = db["rules"].get(section["parent"])
        plabel = (
            f"[{section['parent']}] {parent['title']}" if parent else section["parent"]
        )
        print(f"Parent: {plabel}")
    if section["children"]:
        kids = section["children"]
        suffix = " …" if len(kids) > 12 else ""
        print(f"Sub-sections ({len(kids)}): {', '.join(kids[:12])}{suffix}")
    print(_divider("─"))
    if component is not None:
        component_text = _format_component(component)
        if component_text:
            print(component_text)
            print(_divider("·"))

    print()
    print(_wrap(section["text"]))
    if section["links_out"]:
        refs = section["links_out"][:8]
        suffix = " …" if len(section["links_out"]) > 8 else ""
        print(f"\nSee also: {', '.join(f'[{r}]' for r in refs)}{suffix}")
    print()


def cmd_search(db: dict, term: str, *, json_mode: bool, _emb_path: Path | None = None) -> None:
    """rorcli search <term> — hybrid semantic + full-text search across sections and glossary."""
    term_lower = term.lower()

    # --- Load embeddings (optional; falls back to keyword-only if absent) ---
    from rorcli.embeddings import load_embeddings, semantic_scores

    if _emb_path is None:
        # Default: alongside the DB, inferred from the DB's own location
        # We don't have the DB path here, so we use the package-relative default.
        _pkg = Path(__file__).parent
        _emb_path = _pkg / "rorcli.embeddings.npz"

    emb_ids, emb_vectors = load_embeddings(_emb_path)
    sem_scores: dict[str, float] = {}
    if emb_ids is not None and emb_vectors is not None:
        sem_scores = semantic_scores(term, emb_ids, emb_vectors)

    _SEMANTIC_THRESHOLD = 0.35
    _KW_MAX = 15.0
    _W_SEM = 0.6
    _W_KW = 0.4

    def _hybrid(item_id: str, kw_score: int) -> float:
        kw_norm = min(kw_score, _KW_MAX) / _KW_MAX
        sem = sem_scores.get(item_id, 0.0)
        return _W_SEM * sem + _W_KW * kw_norm

    # --- Gather keyword scores ---

    # Glossary keyword scores
    glossary_kw: dict[str, int] = {}
    for t, entry in db["glossary"].items():
        if term_lower in t.lower():
            glossary_kw[t] = 10

    # Rules section keyword scores
    section_kw: dict[str, int] = {}
    for sid, section in db["rules"].items():
        score = 0
        if term_lower in section["title"].lower():
            score += 10
        text_lower = section.get("text", "").lower()
        if term_lower in text_lower:
            score += max(1, min(5, text_lower.count(term_lower)))
        if score:
            section_kw[sid] = score

    # Component keyword scores
    component_kw: dict[str, int] = {}  # item_id → score
    for comp_type, components in db.get("components", {}).items():
        if not isinstance(components, dict):
            continue
        for slug, component in components.items():
            if not isinstance(component, dict):
                continue
            score = 0
            name = component.get("name", "")
            if term_lower in name.lower():
                score += 10
            search_text = _component_search_text(component).lower()
            if term_lower in search_text:
                score += max(1, min(5, search_text.count(term_lower)))
            if score:
                item_id = _component_id(comp_type, slug)
                component_kw[item_id] = score

    # --- Merge: add semantic-only hits (above threshold) ---
    all_section_ids: set[str] = set(db["rules"].keys())
    all_component_ids: set[str] = set()
    for comp_type, components in db.get("components", {}).items():
        if not isinstance(components, dict):
            continue
        for slug in components:
            all_component_ids.add(_component_id(comp_type, slug))

    if sem_scores:
        for item_id, sim in sem_scores.items():
            if sim < _SEMANTIC_THRESHOLD:
                continue
            if item_id.startswith("glossary:"):
                term_key = item_id[len("glossary:"):]
                if term_key not in glossary_kw:
                    glossary_kw[term_key] = 0
            elif item_id in all_section_ids:
                if item_id not in section_kw:
                    section_kw[item_id] = 0
            elif item_id in all_component_ids:
                if item_id not in component_kw:
                    component_kw[item_id] = 0

    # --- Score and rank ---

    # Glossary hits ranked by hybrid score
    glossary_ranked: list[tuple[float, str, dict]] = []
    for t, kw_score in glossary_kw.items():
        entry = db["glossary"][t]
        h = _hybrid(f"glossary:{t}", kw_score)
        glossary_ranked.append((h, t, entry))

    glossary_ranked.sort(key=lambda p: p[0], reverse=True)

    glossary_pairs: list[tuple[float, dict]] = [
        (h, {
            "type": "glossary",
            "term": t,
            "definition": entry["definition"],
            "sections": entry["sections"],
            "score": round(h, 4),
        })
        for h, t, entry in glossary_ranked
    ]

    # Section hits ranked by hybrid score
    section_ranked: list[tuple[float, dict]] = []
    for sid, kw_score in section_kw.items():
        section = db["rules"][sid]
        h = _hybrid(sid, kw_score)
        section_ranked.append((h, section))

    section_ranked.sort(key=lambda p: p[0], reverse=True)

    section_pairs: list[tuple[float, dict]] = [
        (h, {
            "type": "section",
            "id": section["id"],
            "title": section["title"],
            "file": section["file"],
            "score": round(h, 4),
        })
        for h, section in section_ranked
    ]

    # Component hits ranked by hybrid score
    def _comp_type_slug(item_id: str) -> tuple[str, str, dict] | None:
        for prefix, comp_type in _COMPONENT_PREFIXES.items():
            if item_id.startswith(prefix + "-"):
                slug = item_id[len(prefix) + 1:]
                component = db.get("components", {}).get(comp_type, {}).get(slug)
                if component is not None:
                    return comp_type, slug, component
        # misc
        component = db.get("components", {}).get("misc", {}).get(item_id)
        if component is not None:
            return "misc", item_id, component
        return None

    component_ranked: list[tuple[float, str, str, dict]] = []
    for item_id, kw_score in component_kw.items():
        info = _comp_type_slug(item_id)
        if info is None:
            continue
        comp_type, slug, component = info
        h = _hybrid(item_id, kw_score)
        component_ranked.append((h, comp_type, slug, component))

    component_ranked.sort(key=lambda p: p[0], reverse=True)

    component_pairs: list[tuple[float, dict]] = [
        (h, {
            "type": "component",
            "id": _component_id(comp_type, slug),
            "name": _component_display_name(component),
            "comp_type": comp_type,
            "score": round(h, 4),
        })
        for h, comp_type, slug, component in component_ranked
    ]

    all_ranked = glossary_pairs + section_pairs + component_pairs
    all_ranked.sort(key=lambda p: p[0], reverse=True)
    results = [r for _, r in all_ranked[:20]]

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
        elif r["type"] == "component":
            print(f"\n[{r['id']}]  {r['name']}  ({r['comp_type']})  (score {r['score']})")
        else:
            print(f"\n[{r['id']}]  {r['title']}  (score {r['score']})")
            print(f"  {r['file']}")
    print()
