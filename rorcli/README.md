# rorcli

A CLI tool for querying Republic of Rome game data. Parses Markdown rulebook and component files into a structured JSON database, then exposes section lookup and full-text search.

---

## Setup

Run from the **repo root**. Build before querying.

```bash
python -m rorcli build
```

Parses `game-data/rules/` (rules) and `game-data/components/` (cards, tables) and writes `rorcli/rorcli.db.json` (gitignored).

**Build options:**

```
--rules-dir PATH       Override rules directory (default: game-data/rules/)
--components-dir PATH  Override components directory (default: game-data/components/)
--output PATH          Override output path (default: rorcli/rorcli.db.json)
--json                 Print a JSON summary instead of human-readable output
```

---

## Commands

All query commands accept `--json` (machine-readable output) and `--db PATH` (non-default database).

### `show`

Display the full text of a section by its code.

```bash
python -m rorcli show 1.09.4
python -m rorcli show war-1st-punic
python -m rorcli show statesman-1a --json
```

### `search`

Full-text search across section titles, bodies, and glossary terms. Glossary hits are shown first; title matches rank above body matches.

```bash
python -m rorcli search "consul"
python -m rorcli search "Cornelius" --json
```

---

## Section codes

Rules sections use dot-separated numeric codes matching the rulebook hierarchy:

| Code | Meaning |
|---|---|
| `1.09` | Senate Phase |
| `1.09.4` | Censor |
| `1.09.41` | Prosecutions |

Component sections use hyphenated IDs matching the `{#anchor}` in the source file:

| Code | Meaning |
|---|---|
| `senator-early` | Early Republic senator table |
| `statesman-1a` | Scipio Africanus statesman card |
| `war-1st-punic` | 1st Punic War card |
| `table-combat` | Combat Results Table |
