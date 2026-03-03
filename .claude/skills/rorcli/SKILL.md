---
name: rorcli
description: Provides structured, authoritative access to the Republic of Rome Living Rules to understand game rules, mechanics and terminology.
---

## Purpose

Use this skill whenever you need to verify or understand Republic of Rome game rules, mechanics, or terminology. rorcli parses the Republic of Rome Living Rules Markdown files into a queryable database. Always query it rather than relying on assumptions about how the game works.

---

## Invocation

rorcli is registered as an MCP server. Call its tools **directly** — no Bash needed.

| MCP Tool | Equivalent CLI |
|---|---|
| `mcp__rorcli__show` | `rorcli show <section_code>` |
| `mcp__rorcli__search` | `rorcli search <term>` |
| `mcp__rorcli__explain` | `rorcli explain <term>` |
| `mcp__rorcli__context` | `rorcli context <section_code>` |

All tools return JSON automatically — no `--json` flag required.

---

## Commands

### `mcp__rorcli__show` — read a specific section

Use when you know the section code.

Call with `{"section_code": "1.09.4"}`.

Returns the section's full rule text, its parent, children, and cross-reference links (`links_out` / `links_in`). Use `links_out` to follow references to related rules.

---

### `mcp__rorcli__search` — find sections by keyword

Use when you don't know the section code but know a concept or keyword.

Call with `{"term": "mortality"}`.

Returns ranked glossary hits (type `glossary`) and section hits (type `section`). Always check glossary hits first — they give the authoritative term definition and the canonical list of section codes to consult.

---

### `mcp__rorcli__explain` — look up a defined game term

Use when you need the official definition of a game term and all rule sections that govern it.

Call with `{"term": "HRAO"}`.

Returns the glossary definition plus the full text of every section the term references. This is often the single most useful command — it combines definition + rules in one call.

---

### `mcp__rorcli__context` — explore a section's neighbourhood

Use when you have a section but need to understand it in relation to the rules around it (parent scope, sibling options, subsections, and cross-links).

Call with `{"section_code": "1.09.64"}`.

Returns the section plus its `parent`, `siblings`, `children`, `links_out`, and `links_in` — all as full objects, not just codes.

---

## Recommended workflow

1. **Unknown term?** → `explain "<term>"` first.
2. **Unknown section code?** → `search "<keyword>"`, then `show <code>` for the best hit.
3. **Need surrounding rules?** → `context <code>` to see parent scope and siblings.
4. **Need to follow a cross-reference?** → take a code from `links_out` and call `show` on it.
5. **Implementing a mechanic?** → use `explain` on every relevant term, then `context` on the governing section to confirm you have the full picture.

Never guess at rule details. If you are uncertain, query rorcli before writing or modifying game logic.

