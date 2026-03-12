"""
rorcli — Republic of Rome CLI

Usage (run from repo root):
    python -m rorcli build [--rules-dir PATH] [--output PATH] [--json]
    python -m rorcli show <section_code> [--json] [--db PATH]
    python -m rorcli search <term> [--json] [--db PATH]
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
_DEFAULT_COMPONENTS_DIR = _GAME_DATA_DIR / "components"
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
    p_build.add_argument(
        "--components-dir",
        metavar="PATH",
        type=Path,
        default=_DEFAULT_COMPONENTS_DIR,
        help=f"Components directory (default: {_DEFAULT_COMPONENTS_DIR})",
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

    args = parser.parse_args()

    if args.command == "build":
        from rorcli.build import build_database

        output = args.output or _DEFAULT_DB_PATH
        comp_dir = args.components_dir
        if comp_dir is not None and str(comp_dir).strip() == "":
            comp_dir = None
        build_database(
            rules_dir=args.rules_dir,
            output_path=output,
            json_mode=args.json,
            components_dir=comp_dir,
        )
    else:
        from rorcli.query import load_db, cmd_show, cmd_search

        db = load_db(db_path=Path(args.db) if args.db else _DEFAULT_DB_PATH)

        if args.command == "show":
            cmd_show(db, args.section_code, json_mode=args.json)
        elif args.command == "search":
            cmd_search(db, args.term, json_mode=args.json)


if __name__ == "__main__":
    main()
