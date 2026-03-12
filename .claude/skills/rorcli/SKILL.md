---
name: rorcli
description: Provides structured, authoritative access to Republic of Rome rules, card data, and game components (senators, statesmen, wars, concessions, provinces, laws, events, tables).
---

## Purpose

Use this skill whenever you need to verify or understand Republic of Rome rules, mechanics, terminology, or card data. rorcli parses the rulebook and component files into a queryable database. Always query it rather than relying on assumptions about how the game works.

---

## Invocation

rorcli is registered as an MCP server. Call its tools **directly** — no Bash needed.

| MCP Tool | Equivalent CLI |
|---|---|
| `mcp__rorcli__show` | `rorcli show <section_code>` |
| `mcp__rorcli__search` | `rorcli search <term>` |

All tools return JSON automatically — no `--json` flag required.

---

## Commands

### `mcp__rorcli__show` — read a specific section

Use when you know the section code. Two ID formats exist:

- **Rules:** dot-separated numeric — `"1.09.4"`, `"1.10.1"`
- **Components:** hyphenated — `"war-jugurthine"`, `"statesman-1a"`, `"senator-early"`, `"concession-armaments"`, `"province-sicilia"`, `"law-gabinian"`, `"table-combat"`

Call with `{"section_code": "war-jugurthine"}` or `{"section_code": "1.09.4"}`.

Returns the section's full text, its parent, children, and cross-reference links (`links_out` / `links_in`). Use `links_out` to follow references to related rules.

---

### `mcp__rorcli__search` — find sections by keyword or concept

Use when you don't know the section code but know a concept or keyword. Search is **hybrid**: it combines semantic (embedding-based) similarity with keyword matching, so conceptual queries like `"advanced rules random events"` surface relevant results even when the exact term isn't known.

Call with `{"term": "mortality"}` or `{"term": "advanced rules random events"}`.

Returns ranked glossary hits (type `glossary`), section hits (type `section`), and component card hits (type `component`). Always check glossary hits first — they give the authoritative term definition and the canonical list of section codes to consult.

> **Note:** Semantic search requires `fastembed` to be installed and the embeddings file (`rorcli.embeddings.npz`) to be present (built via `rorcli build`). If the embeddings file is absent, search falls back to keyword-only without error.

---

## Recommended workflow

1. **Unknown section code?** → `search "<keyword>"`, then `show <code>` for the best hit.
2. **Need to follow a cross-reference?** → take a code from `links_out` and call `show` on it.
3. **Implementing a mechanic?** → `search` on relevant terms, then `show` on the governing section to confirm you have the full picture.

**Important:** Component sections (wars, senators, provinces, etc.) describe individual component properties only — not the rules governing when or how they are used. For scenario-specific questions, always also check the relevant rules via `show` or `search`.

Never guess at rule details. If you are uncertain, query rorcli before writing or modifying game logic.
