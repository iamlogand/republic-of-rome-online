---
name: rorcli
description: Provides structured, authoritative access to the Republic of Rome rulebook and game components. TRIGGER when: the task involves original board game rules, mechanics, or components in any way. DO NOT TRIGGER when: the task has no need to consult the original rules or component data.
---

Provides structured, authoritative access to the Republic of Rome rulebook and game components. TRIGGER when: the task involves original board game rules, mechanics, or components in any way. DO NOT TRIGGER when: the task has no need to consult the original rules or component data.

## Tools

- `mcp__rorcli__list {"type": "..."}` — list all components of a type (statesmen, wars, senators, provinces, leaders, concessions, laws, events, intrigue, board)
- `mcp__rorcli__search {"term": "..."}` — find sections by keyword or concept; returns ranked glossary, rules, and component hits
- `mcp__rorcli__show {"id": "..."}` — fetch a section by id

## Workflow

0. Need all components of a type? → `list` (e.g. all statesmen, all wars)
1. Don't know the code? → `search`, then `show` the best hit
2. Check `links_out` to follow cross-references to related rules
3. Component sections describe card properties only — also `search` for the governing rules
