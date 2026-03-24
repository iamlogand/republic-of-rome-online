"""rorcli MCP stdio server — wraps Republic of Rome CLI query commands as MCP tools.

Protocol: JSON-RPC 2.0 over stdio (one message per line, UTF-8).
"""

import sys
import json
from pathlib import Path

_REPO_ROOT = Path(__file__).parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from rorcli import query as _query  # noqa: E402


### Tool descriptors ###


_TOOLS = [
    {
        "name": "show",
        "description": "Show the full text of a rules section or component by its ID. Rules use dot-separated IDs (e.g. 1.09.4); components use hyphenated IDs (e.g. war-1st-punic, statesman-1a, senator-1, province-sicilia).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "string",
                    "description": "Section or component ID, e.g. 1.09.4 (rules) or war-jugurthine (component)",
                }
            },
            "required": ["id"],
        },
    },
    {
        "name": "list",
        "description": "List all components of a given type. Valid types: wars, leaders, provinces, laws, events, intrigue, concessions, senators, statesmen, board.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "description": "Component type, e.g. 'statesmen' or 'wars'",
                }
            },
            "required": ["type"],
        },
    },
    {
        "name": "search",
        "description": "Full-text search across rules sections, glossary, and components (wars, senators, provinces, etc.).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "term": {"type": "string", "description": "Search term or phrase"}
            },
            "required": ["term"],
        },
    },
]


### Helpers ###


def _write(obj: dict) -> None:
    sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def _respond(req_id, result: dict) -> None:
    _write({"jsonrpc": "2.0", "id": req_id, "result": result})


def _send_error(req_id, code: int, message: str) -> None:
    _write(
        {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}
    )


### Dispatch ###


def _handle(msg: dict) -> None:
    method = msg.get("method", "")
    req_id = msg.get("id")

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
        return

    if method == "tools/list":
        _respond(req_id, {"tools": _TOOLS})
        return

    if method == "tools/call":
        params = msg.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})
        try:
            if tool_name == "show":
                data = _query.cmd_show(args["id"], json_mode=True)
            elif tool_name == "search":
                data = _query.cmd_search(args["term"], json_mode=True)
            elif tool_name == "list":
                data = _query.cmd_list(args["type"], json_mode=True)
            else:
                _send_error(req_id, -32602, f"Unknown tool: {tool_name!r}")
                return
            _respond(
                req_id,
                {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(data, indent=2, ensure_ascii=False),
                        }
                    ]
                },
            )
        except Exception as exc:
            _send_error(req_id, -32603, str(exc))
        return

    if req_id is not None:
        _send_error(req_id, -32601, "Method not found")


### Main loop ###


def main() -> None:
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
