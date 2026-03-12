"""rorcli MCP stdio server — wraps Republic of Rome CLI query commands as MCP tools.

Protocol: JSON-RPC 2.0 over stdio (one message per line, UTF-8).
"""

import sys
import json
import io
import contextlib
from pathlib import Path

_PACKAGE_DIR = Path(__file__).parent
_DB_PATH = _PACKAGE_DIR / "rorcli.db.json"
_EMB_PATH = _PACKAGE_DIR / "rorcli.embeddings.npz"
_RULES_DIR = _PACKAGE_DIR.parent / "game-data" / "rules"
_COMPONENTS_DIR = _PACKAGE_DIR.parent / "game-data" / "components"

# Ensure the repo root is on sys.path so `from rorcli import query` works
# regardless of the working directory when this script is launched.
_REPO_ROOT = _PACKAGE_DIR.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from rorcli import query as _query  # noqa: E402


### DB (loaded once at startup) ###

_db = _query.load_db(_DB_PATH)


### helpers ###


def _capture(fn, *args):
    """Call fn(*args, json_mode=True), capture stdout, return parsed JSON."""
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            fn(*args, json_mode=True)
    except SystemExit:
        pass
    return json.loads(buf.getvalue())


def _write(obj):
    sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def _respond(req_id, result):
    _write({"jsonrpc": "2.0", "id": req_id, "result": result})


def _send_error(req_id, code, message):
    _write(
        {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}
    )


### Tool descriptors ###


_TOOLS = [
    {
        "name": "show",
        "description": "Show the full text of a rules section by its code (e.g. 1.09.4).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "section_code": {
                    "type": "string",
                    "description": "Section code, e.g. 1.09.12",
                }
            },
            "required": ["section_code"],
        },
    },
    {
        "name": "search",
        "description": "Full-text search across sections and glossary.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "term": {"type": "string", "description": "Search term or phrase"}
            },
            "required": ["term"],
        },
    },
]


### Dispatch ###


def _handle(msg: dict) -> None:
    method = msg.get("method", "")
    req_id = msg.get("id")  # None for notifications

    if method == "initialize":
        _respond(
            req_id,
            {
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": "rorcli", "version": "1.0.0"},
                "capabilities": {"tools": {}},
            },
        )
        return

    if method in ("initialized", "notifications/initialized"):
        return  # notification — no response required

    if method == "tools/list":
        _respond(req_id, {"tools": _TOOLS})
        return

    if method == "tools/call":
        params = msg.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})
        try:
            if tool_name == "show":
                data = _capture(_query.cmd_show, _db, args["section_code"])
            elif tool_name == "search":
                data = _capture(_query.cmd_search, _db, args["term"])
            else:
                _send_error(req_id, -32602, f"Unknown tool: {tool_name!r}")
                return
            text = json.dumps(data, indent=2, ensure_ascii=False)
            _respond(req_id, {"content": [{"type": "text", "text": text}]})
        except Exception as exc:
            _send_error(req_id, -32603, str(exc))
        return

    # Unknown method — only send error for requests (with id), not notifications
    if req_id is not None:
        _send_error(req_id, -32601, "Method not found")


### Main loop ###


def main():
    # Ensure UTF-8 I/O on Windows
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            _send_error(None, -32700, "Parse error")
            continue
        _handle(msg)


if __name__ == "__main__":
    main()
