"""Build semantic embeddings for rorcli.

Uses fastembed (BAAI/bge-small-en-v1.5, 384-dim) stored in a numpy .npz file
alongside rorcli.db.json. Silently skips if fastembed or numpy is unavailable.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np

from rorcli.parsers.components import component_id as _component_id, component_search_text as _component_search_text


def _collect_items(db: dict) -> tuple[list[str], list[str]]:
    """Return parallel (ids, texts) lists for every embeddable item in the DB."""
    ids: list[str] = []
    texts: list[str] = []

    # Rules sections
    for sid, section in db.get("rules", {}).items():
        title = section.get("title", "")
        text = section.get("text", "")
        ids.append(sid)
        texts.append(f"{title}\n{text}" if text else title)

    # Glossary terms
    for term, entry in db.get("glossary", {}).items():
        defn = entry.get("definition", "")
        ids.append(f"glossary:{term}")
        texts.append(f"{term}: {defn}")

    # Components
    for component_type, components in db.get("components", {}).items():
        if not isinstance(components, dict):
            continue
        for slug, component in components.items():
            if not isinstance(component, dict):
                continue
            item_id = _component_id(component_type, slug)
            ids.append(item_id)
            texts.append(_component_search_text(component) or component.get("name", slug))

    return ids, texts


def build_embeddings(db: dict, emb_path: Path) -> None:
    """Embed all DB items and save to *emb_path* (numpy .npz).

    Silently skips if fastembed or numpy is unavailable.
    """
    try:
        import numpy as np
        from fastembed import TextEmbedding
    except ImportError:
        return

    ids, texts = _collect_items(db)
    if not ids:
        return

    model = TextEmbedding("BAAI/bge-small-en-v1.5")
    # embed() returns a generator of numpy arrays
    vectors = np.array(list(model.embed(texts)), dtype=np.float32)

    emb_path = Path(emb_path)
    emb_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(str(emb_path), ids=np.array(ids), vectors=vectors)
