# rorcli

CLI tool for querying Republic of Rome rules and component data.

## Usage

Run from repo root. Build the database and embeddings first, then query using `search` and `show`.

```bash
python -m rorcli build
python -m rorcli search "consul"
python -m rorcli show 1.09.4
python -m rorcli show war-1st-punic --json
```

## Codes

- **Rules:** dot-separated — `1.09`, `1.09.4`, `1.09.41`
- **Components:** hyphenated — `war-1st-punic`, `statesman-1a`, `senator-1`, `province-sicilia`
