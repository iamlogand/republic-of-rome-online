"""
Build step: parse all Markdown rulebook files → rorcli/rorcli.db.json
"""

import datetime
import json
import sys
from pathlib import Path

from rorcli.parsers.rules import (
    NAV_FILENAMES,
    GLOSSARY_FILE,
    parse_sections_from_file,
    parse_glossary,
    compute_parent,
    extract_refs,
)
from rorcli.parsers.senators import parse_senators
from rorcli.parsers.statesmen import parse_statesmen
from rorcli.parsers.concessions import parse_concessions
from rorcli.parsers.events import parse_events
from rorcli.parsers.intrigue import parse_intrigue
from rorcli.parsers.laws import parse_laws
from rorcli.parsers.wars import parse_wars
from rorcli.parsers.leaders import parse_leaders
from rorcli.parsers.provinces import parse_provinces
from rorcli.parsers.board import parse_board
from rorcli.parsers.misc import parse_misc


### Main build function ###


def build_database(
    rules_dir: Path,
    output_path: Path,
    json_mode: bool,
    components_dir=None,
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
        print(f"Building rorcli database…")

    all_rules: dict[str, dict] = {}
    glossary: dict = {}
    index: dict = {}
    rules_file_count = 0

    for filepath in sorted(rules_dir.rglob("*.md")):
        filename = filepath.name

        if filename in NAV_FILENAMES:
            continue

        if filename == GLOSSARY_FILE:
            glossary, index = parse_glossary(filepath)
            continue

        sections = parse_sections_from_file(filepath, rules_dir)
        for s in sections:
            all_rules[s["id"]] = s
        if sections:
            rules_file_count += 1

    # Parse component files (structured data only — not added to rules index)
    components_data: dict = {}
    if components_dir is not None:
        components_dir = Path(components_dir).resolve()
        if components_dir.exists():
            _component_files = [
                ("senators",    "senators.md",    parse_senators),
                ("statesmen",   "statesmen.md",   parse_statesmen),
                ("wars",        "wars.md",         parse_wars),
                ("leaders",     "leaders.md",      parse_leaders),
                ("provinces",   "provinces.md",    parse_provinces),
                ("concessions", "concessions.md",  parse_concessions),
                ("events",      "events.md",       parse_events),
                ("intrigue",    "intrigue.md",     parse_intrigue),
                ("laws",        "laws.md",         parse_laws),
                ("board",       "board.md",        parse_board),
                ("misc",        "misc.md",         parse_misc),
            ]
            for key, filename, parser in _component_files:
                f = components_dir / filename
                if f.exists():
                    components_data[key] = parser(f)

    # Parent/child relationships
    all_ids = set(all_rules)
    for sid, section in all_rules.items():
        parent = compute_parent(sid, all_ids)
        section["parent"] = parent
        if parent and parent in all_rules:
            all_rules[parent]["children"].append(sid)

    for section in all_rules.values():
        section["children"].sort()

    # Cross-references (links_out / links_in)
    for sid, section in all_rules.items():
        raw_refs = extract_refs(section.get("text", ""))
        section["links_out"] = [r for r in raw_refs if r in all_ids and r != sid]

        for ref in section["links_out"]:
            if sid not in all_rules[ref]["links_in"]:
                all_rules[ref]["links_in"].append(sid)

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)

    db = {
        "meta": {
            "built_at": datetime.datetime.utcnow().isoformat() + "Z",
            "rules_dir": str(rules_dir),
            "components_dir": str(components_dir) if components_dir is not None else None,
            "total_rules": len(all_rules),
            "total_glossary_terms": len(glossary),
        },
        "rules": all_rules,
        "glossary": glossary,
        "index": index,
        "components": components_data,
    }

    output_path.write_text(
        json.dumps(db, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Build semantic embeddings (requires fastembed; silently skipped if absent)
    from rorcli.embeddings import build_embeddings

    # rorcli.db.json → rorcli.embeddings.npz (strip both suffixes, add new one)
    emb_path = output_path.with_name(output_path.name.split(".")[0] + ".embeddings.npz")
    if not json_mode:
        print(f"  Rules        {len(all_rules)} sections ({rules_file_count} files)")
        print(f"  Glossary     {len(glossary)} terms · {len(index)} index entries")
        if components_data:
            comp_parts = [f"{k} {len(v)}" for k, v in components_data.items() if isinstance(v, dict)]
            print(f"  Components   {' · '.join(comp_parts)}")
        print(f"  Written      {output_path.name}")
        print()
        print(f"Building embeddings (this may take a few minutes)…", end=" ", flush=True)

    try:
        build_embeddings(db, emb_path)
        if not json_mode:
            if emb_path.exists():
                print(f"done")
                print(f"  Written      {emb_path.name}")
            else:
                print("skipped (fastembed not installed)")
    except Exception as exc:  # pragma: no cover
        if not json_mode:
            print(f"failed ({exc})")

    if json_mode:
        print(
            json.dumps(
                {
                    "status": "ok",
                    "output": str(output_path),
                    "rules": len(all_rules),
                    "glossary_terms": len(glossary),
                    "index_entries": len(index),
                }
            )
        )
