"""
rorcli — Republic of Rome CLI

Usage (run from repo root):
    python -m rorcli build
    python -m rorcli show <id> [--json]
    python -m rorcli search <term> [--json]
"""

import argparse
import io
import json
import sys

from rorcli.build import build
from rorcli.query import cmd_show, cmd_search

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


def main():
    parser = argparse.ArgumentParser(
        prog="rorcli",
        description="Republic of Rome CLI-based game data query tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    sub = parser.add_subparsers(dest="command", metavar="COMMAND")
    sub.required = True

    sub.add_parser("build", help="Parse game data to build the database and embeddings")

    p_search = sub.add_parser("search", help="Full-text search of rules and components")
    p_search.add_argument("term", help="Search term or phrase")
    p_search.add_argument("--json", action="store_true", help="Output as JSON")

    p_show = sub.add_parser("show", help="Show a rule or component")
    p_show.add_argument("id", help="Rule or component ID")
    p_show.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if args.command == "build":
        build()
    elif args.command == "show":
        result = cmd_show(args.id, json_mode=args.json)
        if result is not None:
            print(json.dumps(result, indent=2, ensure_ascii=False))
            if "error" in result:
                sys.exit(1)
    elif args.command == "search":
        result = cmd_search(args.term, json_mode=args.json)
        if result is not None:
            print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
