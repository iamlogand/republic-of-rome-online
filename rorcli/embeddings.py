from __future__ import annotations

from pathlib import Path

import numpy as np
from fastembed import TextEmbedding

from rorcli.parsers.components import (
    component_id,
    component_search_text,
)


def _collect_items(db: dict) -> tuple[list[str], list[str]]:
    ids: list[str] = []
    texts: list[str] = []

    for id, rule in db.get("rules", {}).items():
        title = rule.get("title", "")
        text = rule.get("text", "")
        ids.append(id)
        texts.append(f"{title}\n{text}" if text else title)

    for term, entry in db.get("glossary", {}).items():
        definition = entry.get("definition", "")
        ids.append(f"glossary:{term}")
        texts.append(f"{term}: {definition}")

    for component_type, components in db.get("components", {}).items():
        if not isinstance(components, dict):
            continue
        for slug, component in components.items():
            if not isinstance(component, dict):
                continue
            item_id = component_id(component_type, slug)
            ids.append(item_id)
            texts.append(
                component_search_text(component) or component.get("name", slug)
            )

    return ids, texts


def build_embeddings(db: dict, output_filepath: Path) -> None:
    ids, texts = _collect_items(db)
    if not ids:
        return

    model = TextEmbedding("BAAI/bge-small-en-v1.5")
    vectors = np.array(list(model.embed(texts)), dtype=np.float32)

    output_filepath = Path(output_filepath)
    output_filepath.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(str(output_filepath), ids=np.array(ids), vectors=vectors)
