"""
Build step: parse all Markdown rulebook files → rorcli/rorcli.db.json
"""

import datetime
import json
import sys
from pathlib import Path

from rorcli.parsers.rules import parse_rules
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


def build() -> None:
    _pkg = Path(__file__).parent
    _game_data = _pkg.parent / "game-data"
    rules_dir = (_game_data / "rules").resolve()
    output_path = (_pkg / "rorcli.db.json").resolve()
    components_dir = (_game_data / "components").resolve()

    if not rules_dir.exists():
        print(f"Error: Rules directory not found: {rules_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Building rorcli database…")

    all_rules, glossary, index = parse_rules(rules_dir)

    # Parse component files (structured data only — not added to rules index)
    components_data: dict = {}
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

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)

    db = {
        "meta": {
            "built_at": datetime.datetime.utcnow().isoformat() + "Z",
            "rules_dir": str(rules_dir),
            "components_dir": str(components_dir),
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
    print(f"  Rules        {len(all_rules)} sections")
    print(f"  Glossary     {len(glossary)} terms · {len(index)} index entries")
    if components_data:
        comp_parts = [f"{k} {len(v)}" for k, v in components_data.items() if isinstance(v, dict)]
        print(f"  Components   {' · '.join(comp_parts)}")
    print(f"  Written      {output_path.name}")
    print()
    print(f"Building embeddings (this may take a few minutes)…", end=" ", flush=True)

    try:
        build_embeddings(db, emb_path)
        if emb_path.exists():
            print(f"done")
            print(f"  Written      {emb_path.name}")
        else:
            print("skipped (fastembed not installed)")
    except Exception as exc:  # pragma: no cover
        print(f"failed ({exc})")
