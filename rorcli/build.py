import datetime
import json
import sys
from pathlib import Path

from rorcli.parsers.rules import parse_rulebook
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
from rorcli.embeddings import build_embeddings


def build() -> None:
    package_path = Path(__file__).parent
    game_data_path = package_path.parent / "game-data"
    rules_path = (game_data_path / "rules").resolve()
    components_path = (game_data_path / "components").resolve()
    database_output_filepath = (package_path / "rorcli.db.json").resolve()
    embeddings_output_filepath = (package_path / "rorcli.emb.npz").resolve()

    if not rules_path.exists():
        print(f"Error: Rules directory not found: {rules_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Building rorcli database…")

    rules, glossary = parse_rulebook(rules_path)

    components: dict = {}
    if components_path.exists():
        component_files = [
            ("senators", "senators.md", parse_senators),
            ("statesmen", "statesmen.md", parse_statesmen),
            ("wars", "wars.md", parse_wars),
            ("leaders", "leaders.md", parse_leaders),
            ("provinces", "provinces.md", parse_provinces),
            ("concessions", "concessions.md", parse_concessions),
            ("events", "events.md", parse_events),
            ("intrigue", "intrigue.md", parse_intrigue),
            ("laws", "laws.md", parse_laws),
            ("board", "board.md", parse_board),
            ("misc", "misc.md", parse_misc),
        ]
        for key, filename, parser in component_files:
            filepath = components_path / filename
            if filepath.exists():
                components[key] = parser(filepath)

    db = {
        "meta": {
            "built_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        },
        "rules": rules,
        "glossary": glossary,
        "components": components,
    }

    database_output_filepath.write_text(
        json.dumps(db, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"  Rules        {len(rules)} sections")
    print(f"  Glossary     {len(glossary)} terms")
    if components:
        comp_parts = [
            f"{k} {len(v)}" for k, v in components.items() if isinstance(v, dict)
        ]
        print(f"  Components   {' · '.join(comp_parts)}")
    print(f"  Written      {database_output_filepath.name}")
    print()
    print(f"Building embeddings (this may take a few minutes)…", end=" ", flush=True)
    time = datetime.datetime.now()
    build_embeddings(db, embeddings_output_filepath)
    elapsed = int((datetime.datetime.now() - time).total_seconds())
    print(f"done (took {elapsed // 60}m {elapsed % 60}s)")
    print(f"  Written      {embeddings_output_filepath.name}")
