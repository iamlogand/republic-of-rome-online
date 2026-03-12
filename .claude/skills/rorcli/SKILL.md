---
name: rorcli
description: Provides structured, authoritative access to Republic of Rome rules and game components (senators, statesmen, wars, concessions, provinces, laws, events, tables).
---

Query the rulebook and component database. Always use this rather than guessing at rules or card data.

## Tools

- `mcp__rorcli__search {"term": "..."}` — find sections by keyword or concept; returns ranked glossary, rules, and component hits
- `mcp__rorcli__show {"section_code": "..."}` — fetch a section by code

## ID formats

- Rules: `"1.09.4"`
- Components: `"war-jugurthine"`, `"senator-1"`, `"statesman-1a"`, `"province-sicilia"``

## Workflow

1. Don't know the code? → `search`, then `show` the best hit
2. Check `links_out` to follow cross-references to related rules
3. Component sections describe card properties only — also `search` for the governing rules
