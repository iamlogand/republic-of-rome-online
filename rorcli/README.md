# rorcli

CLI tool for querying Republic of Rome rules and component data.

## Usage

Run from repo root. Build the database and embeddings first, then query using `search` and `show`.

```bash
python -m rorcli build
python -m rorcli list statesmen
python -m rorcli list wars --json
python -m rorcli search "consul"
python -m rorcli show 1.09.4
python -m rorcli show war-1st-punic --json
```

## IDs

- **Rules:** dot-separated — `1.09`, `1.09.4`, `1.09.41`
- **Components:** hyphenated — `war-1st-punic`, `statesman-1a`, `senator-1`, `province-sicilia`

## Component types

Valid types for the `list` command: `wars`, `leaders`, `provinces`, `laws`, `events`, `intrigue`, `concessions`, `senators`, `statesmen`, `board`.
