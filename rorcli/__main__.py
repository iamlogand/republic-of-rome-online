"""
rorcli — Republic of Rome CLI

Usage (run from repo root):
    python -m rorcli build [--rules-dir PATH] [--output PATH] [--json]
    python -m rorcli show <section_code> [--json] [--db PATH]
    python -m rorcli search <term> [--json] [--db PATH]
    python -m rorcli explain <term> [--json] [--db PATH]
    python -m rorcli context <section_code> [--json] [--db PATH]
"""

import argparse
import io
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows (box-drawing chars, arrows, etc.)
if isinstance(sys.stdout, io.TextIOWrapper) and sys.stdout.encoding.lower() not in (
    "utf-8",
    "utf-8-sig",
):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if isinstance(sys.stderr, io.TextIOWrapper) and sys.stderr.encoding.lower() not in (
    "utf-8",
    "utf-8-sig",
):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# Default locations relative to this file's position inside rorcli/ (repo root)
_PACKAGE_DIR = Path(__file__).parent  # rorcli/
_GAME_DATA_DIR = _PACKAGE_DIR.parent / "game-data"
_DEFAULT_RULES_DIR = _GAME_DATA_DIR / "rules"
_DEFAULT_DB_PATH = _PACKAGE_DIR / "rorcli.db.json"


def main():
    parser = argparse.ArgumentParser(
        prog="rorcli",
        description="Republic of Rome game data — build and query tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    sub = parser.add_subparsers(dest="command", metavar="COMMAND")
    sub.required = True

    p_build = sub.add_parser(
        "build", help="Parse Markdown rules and build the database"
    )
    p_build.add_argument(
        "--rules-dir",
        metavar="PATH",
        type=Path,
        default=_DEFAULT_RULES_DIR,
        help=f"Rules directory (default: {_DEFAULT_RULES_DIR})",
    )
    p_build.add_argument(
        "--output",
        metavar="PATH",
        type=Path,
        default=None,
        help=f"Output path for database (default: {_DEFAULT_DB_PATH})",
    )
    p_build.add_argument("--json", action="store_true", help="Output result as JSON")

    def _add_flags(p: argparse.ArgumentParser) -> None:
        """Add --json / --db to a subparser so they can follow the subcommand name."""
        p.add_argument("--json", action="store_true", help="Output as JSON")
        p.add_argument(
            "--db", metavar="PATH", default=None, help="Path to rorcli.db.json"
        )

    p_show = sub.add_parser("show", help="Show a section by its code")
    p_show.add_argument("section_code", help="Section code, e.g. 1.09.12")
    _add_flags(p_show)

    p_search = sub.add_parser(
        "search", help="Full-text search across sections and glossary"
    )
    p_search.add_argument("term", help="Search term or phrase")
    _add_flags(p_search)

    p_explain = sub.add_parser(
        "explain", help="Look up a glossary term and show its sections"
    )
    p_explain.add_argument("term", help="Glossary term to explain")
    _add_flags(p_explain)

    p_context = sub.add_parser(
        "context",
        help="Show a section together with its parent, siblings, children, and links",
    )
    p_context.add_argument("section_code", help="Section code, e.g. 1.09.12")
    _add_flags(p_context)

    args = parser.parse_args()

    if args.command == "build":
        from rorcli.build import build_database

        output = args.output or _DEFAULT_DB_PATH
        build_database(
            rules_dir=args.rules_dir,
            output_path=output,
            json_mode=args.json,
        )
    else:
        from rorcli.query import load_db, cmd_show, cmd_search, cmd_explain, cmd_context

        db = load_db(db_path=Path(args.db) if args.db else _DEFAULT_DB_PATH)

        if args.command == "show":
            cmd_show(db, args.section_code, json_mode=args.json)
        elif args.command == "search":
            cmd_search(db, args.term, json_mode=args.json)
        elif args.command == "explain":
            cmd_explain(db, args.term, json_mode=args.json)
        elif args.command == "context":
            cmd_context(db, args.section_code, json_mode=args.json)


if __name__ == "__main__":
    main()
