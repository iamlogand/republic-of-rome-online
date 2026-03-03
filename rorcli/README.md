# rorcli

A CLI tool for querying Republic of Rome game data. Parse the Markdown rulebook files into a structured JSON database, then query sections, search terms, look up glossary entries, and explore the rule hierarchy — in both human-readable and machine-readable form.

---

## Setup

The tool has two layers: a **build step** that parses the source files, and a **query layer** that reads the generated database. You must build before querying.

Run all commands from the **repo root**:

```bash
python -m rorcli build
```

This parses all files under `game-data/rules/` and writes `rorcli/rorcli.db.json` (gitignored).

### Options

```
python -m rorcli build [--rules-dir PATH] [--output PATH] [--json]

  --rules-dir PATH   Override the rules directory (default: game-data/rules/)
  --output PATH      Override the output path (default: rorcli/rorcli.db.json)
  --json             Print a JSON summary instead of human-readable output
```

---

## Commands

All query commands accept `--json` to output machine-readable JSON, and `--db PATH` to point at a non-default database file.

### `show`

Display the full text of a section by its code.

```bash
python -m rorcli show 1.09.4
python -m rorcli show 1.09.4 --json
```

Output includes: title, file, parent, sub-section list, body text, and cross-references.

---

### `search`

Full-text search across section titles, section bodies, and glossary terms.

```bash
python -m rorcli search "consul"
python -m rorcli search "mortality" --json
```

Results are ranked by relevance (title matches score higher than body matches). Glossary hits are shown first if the search term matches a glossary entry.

---

### `explain`

Look up a glossary term and show its definition alongside the text of every section it references.

```bash
python -m rorcli explain "HRAO"
python -m rorcli explain "Civil War" --json
```

Matching is case-insensitive. Falls back to a partial match if no exact match is found (e.g. `explain "consul"` will match `Consul For Life` if `Consul` has no entry of its own).

---

### `context`

Show a section in its structural context: parent, siblings, sub-sections, and cross-reference links in both directions.

```bash
python -m rorcli context 1.09.64
python -m rorcli context 1.09 --json
```

Useful for navigating the rule hierarchy without knowing the exact section codes of neighbouring sections.

---

## Section codes

Section codes follow the numbering scheme used in the rulebook. They are hierarchical — each dot-segment adds one level of depth.

| Code | Meaning |
|---|---|
| `1.09` | Senate Phase (top-level chapter section) |
| `1.09.4` | Censor (first-level subsection) |
| `1.09.41` | Prosecutions (second-level subsection) |
| `1.09.411` | Major Prosecutions (third-level) |
| `4.05.31` | Adequate Force (solitaire/two-player section) |

Parent relationships are inferred from the numeric hierarchy: `1.09.41` is a child of `1.09.4`, which is a child of `1.09`.

