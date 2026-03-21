import json
import sys
import textwrap
from pathlib import Path
from typing import Any

import numpy as np
from fastembed import TextEmbedding
from rorcli.parsers.components import (
    COMPONENT_PREFIXES as _COMPONENT_PREFIXES,
    component_id,
    component_search_text,
)


_DEFAULT_DB_PATH = Path(__file__).parent / "rorcli.db.json"


def semantic_scores(
    query: str,
    ids: list[str],
    vectors: np.ndarray,
) -> dict[str, float]:
    model = TextEmbedding("BAAI/bge-small-en-v1.5")
    q_vec = np.array(list(model.embed([query])), dtype=np.float32)[0]
    sims = vectors.dot(q_vec)
    return {item_id: float(sim) for item_id, sim in zip(ids, sims)}


def load_embeddings(emb_path: Path) -> tuple[list[str], np.ndarray]:
    if not emb_path.exists():
        raise FileNotFoundError(
            f"Embeddings not found at {emb_path} — run 'rorcli build' first."
        )
    data = np.load(str(emb_path), allow_pickle=False)
    ids: list[str] = data["ids"].tolist()
    vectors: np.ndarray = data["vectors"]
    return ids, vectors


def _get_db() -> dict[str, Any]:
    if not _DEFAULT_DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found at {_DEFAULT_DB_PATH} — run 'rorcli build' first."
        )
    return json.loads(_DEFAULT_DB_PATH.read_text(encoding="utf-8"))


def _wrap(text: str, width: int = 88, indent: str = "") -> str:
    paragraphs = text.split("\n\n")
    wrapped = []
    for paragraph in paragraphs:
        lines = paragraph.splitlines()
        if lines and lines[0].lstrip().startswith(("-", "*", ">", "#")):
            wrapped.append(paragraph)
        else:
            collapsed = " ".join(line.strip() for line in lines if line.strip())
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


def _lookup_component(
    db: dict, item_id: str
) -> tuple[str, str, dict] | tuple[None, None, None]:
    components = db.get("components", {})
    for prefix, component_type in _COMPONENT_PREFIXES.items():
        if item_id.startswith(prefix + "-"):
            slug = item_id[len(prefix) + 1 :]
            component = components.get(component_type, {}).get(slug)
            if component is not None:
                return component_type, slug, component
    component = components.get("misc", {}).get(item_id)
    if component is not None:
        return "misc", item_id, component
    return None, None, None


def _format_component(component: dict) -> str:
    skip = {"name", "notes", "description", "text", "title", "special"}
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
    return component["name"]


def _component_body(component: dict) -> str:
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


def _print_component_only(item_id: str, component: dict) -> None:
    print()
    print(_divider("═"))
    print(f"[{item_id}]  {_component_display_name(component)}")
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


def _print_section(section: dict, component: dict | None, rules: dict) -> None:
    print()
    print(_divider("═"))
    print(_section_header(section))
    print(_divider("─"))
    if section["parent"]:
        parent = rules.get(section["parent"])
        plabel = (
            f"[{section['parent']}] {parent['title']}" if parent else section["parent"]
        )
        print(f"Parent: {plabel}")
    prev_id = section.get("prev")
    next_id = section.get("next")
    if prev_id or next_id:
        prev_part = f"← Prev: [{prev_id}]" if prev_id else ""
        next_part = f"Next: [{next_id}] →" if next_id else ""
        print("  ".join(p for p in [prev_part, next_part] if p))
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


def _print_search_results(term: str, results: list[dict]) -> None:
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
            if defn_short:
                print(f"  {defn_short}")
            if r["rule_ids"]:
                suffix = " …" if len(r["rule_ids"]) > 6 else ""
                print(f"  Sections: {', '.join(r['rule_ids'][:6])}{suffix}")
        elif r["type"] == "component":
            print(f"\n[{r['id']}]  {r['name']}  ({r['component_type']})")
        else:
            print(f"\n[{r['id']}]  {r['title']}")
    print()


def cmd_show(item_id: str, *, json_mode: bool) -> dict | None:
    db = _get_db()
    section = db["rules"].get(item_id)
    component = _lookup_component(db, item_id)[2]

    if section is None and component is None:
        if json_mode:
            return {"error": f"{item_id!r} not found."}
        print(f"Error: {item_id!r} not found.", file=sys.stderr)
        sys.exit(1)

    if section is None:
        assert component is not None
        if json_mode:
            return {"id": item_id, "component": component}
        _print_component_only(item_id, component)
        return None

    if json_mode:
        output = {k: v for k, v in section.items() if k != "file"}
        if component is not None:
            output["component"] = component
        return output

    _print_section(section, component, db["rules"])
    return None


_SEMANTIC_THRESHOLD = 0.35
_KW_MAX = 15.0
_W_SEM = 0.6
_W_KW = 0.4


def _keyword_scores(
    db: dict, search_term_lower: str
) -> tuple[dict[str, int], dict[str, int], dict[str, tuple[int, str, str, dict]]]:
    glossary_kw: dict[str, int] = {}
    for term, entry in db["glossary"].items():
        score = 0
        if search_term_lower in term.lower():
            score += 10
        definition = entry.get("definition", "").lower()
        if search_term_lower in definition:
            score += max(1, min(5, definition.count(search_term_lower)))
        if score:
            glossary_kw[term] = score

    section_kw: dict[str, int] = {}
    for rule_id, rule in db["rules"].items():
        score = 0
        if search_term_lower in rule["title"].lower():
            score += 10
        text_lower = rule.get("text", "").lower()
        if search_term_lower in text_lower:
            score += max(1, min(5, text_lower.count(search_term_lower)))
        if score:
            section_kw[rule_id] = score

    component_kw: dict[str, tuple[int, str, str, dict]] = {}
    for component_type, components in db.get("components", {}).items():
        if not isinstance(components, dict):
            continue
        for slug, component in components.items():
            if not isinstance(component, dict):
                continue
            score = 0
            name = component.get("name", "")
            if search_term_lower in name.lower():
                score += 10
            search_text = component_search_text(component).lower()
            if search_term_lower in search_text:
                score += max(1, min(5, search_text.count(search_term_lower)))
            if score:
                item_id = component_id(component_type, slug)
                component_kw[item_id] = (score, component_type, slug, component)

    return glossary_kw, section_kw, component_kw


def cmd_search(search_term: str, *, json_mode: bool) -> dict | None:
    db = _get_db()
    search_term_lower = search_term.lower()

    _pkg = Path(__file__).parent
    emb_path = _pkg / "rorcli.emb.npz"

    emb_ids, emb_vectors = load_embeddings(emb_path)
    sem_scores = semantic_scores(search_term, emb_ids, emb_vectors)

    def _hybrid(item_id: str, kw_score: int) -> float:
        kw_norm = min(kw_score, _KW_MAX) / _KW_MAX
        sem = sem_scores.get(item_id, 0.0)
        return _W_SEM * sem + _W_KW * kw_norm

    glossary_kw, section_kw, component_kw = _keyword_scores(db, search_term_lower)

    for item_id, sim in sem_scores.items():
        if sim < _SEMANTIC_THRESHOLD:
            continue
        if item_id.startswith("glossary:"):
            term_key = item_id[len("glossary:") :]
            if term_key not in glossary_kw:
                glossary_kw[term_key] = 0
        elif item_id in db["rules"]:
            if item_id not in section_kw:
                section_kw[item_id] = 0
        else:
            ctype, cslug, comp = _lookup_component(db, item_id)
            if (
                ctype is not None
                and cslug is not None
                and comp is not None
                and item_id not in component_kw
            ):
                component_kw[item_id] = (0, ctype, cslug, comp)

    glossary_ranked = sorted(
        [
            (
                _hybrid(f"glossary:{term}", kw_score),
                {
                    "type": "glossary",
                    "term": term,
                    "definition": db["glossary"][term]["definition"],
                    "rule_ids": db["glossary"][term]["rule_ids"],
                },
            )
            for term, kw_score in glossary_kw.items()
        ],
        key=lambda p: p[0],
        reverse=True,
    )

    section_ranked = sorted(
        [
            (
                _hybrid(rule_id, kw_score),
                {
                    "type": "rule",
                    "id": db["rules"][rule_id]["id"],
                    "title": db["rules"][rule_id]["title"],
                },
            )
            for rule_id, kw_score in section_kw.items()
        ],
        key=lambda p: p[0],
        reverse=True,
    )

    component_ranked = sorted(
        [
            (
                _hybrid(item_id, kw_score),
                {
                    "type": "component",
                    "id": component_id(ctype, cslug),
                    "name": _component_display_name(comp),
                    "component_type": ctype,
                },
            )
            for item_id, (kw_score, ctype, cslug, comp) in component_kw.items()
        ],
        key=lambda p: p[0],
        reverse=True,
    )

    all_ranked = glossary_ranked + section_ranked + component_ranked
    all_ranked.sort(key=lambda p: p[0], reverse=True)
    results = [r for _, r in all_ranked[:20]]

    if json_mode:
        return {"term": search_term, "results": results}

    _print_search_results(search_term, results)
    return None
