"""
Semantic embeddings for rorcli — build, load, and query.

Uses fastembed (BAAI/bge-small-en-v1.5, 384-dim) stored in a numpy .npz file
alongside rorcli.db.json. All three functions are optional-safe: if fastembed or
numpy is unavailable the caller receives (None, None) / an empty dict and falls
back to keyword-only search.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _component_search_text(component: dict) -> str:
    """Concatenated searchable text for a component (mirrors query.py)."""
    fields = ["name", "description", "text", "special", "effect"]
    parts = [str(component[f]) for f in fields if component.get(f)]
    if "notes" in component:
        parts.extend(component["notes"])
    return " ".join(parts)


def _component_id(comp_type: str, slug: str) -> str:
    """Reconstruct section-style ID for a component (mirrors query.py)."""
    _COMP_TYPE_TO_PREFIX = {
        "wars": "war",
        "leaders": "leader",
        "provinces": "province",
        "laws": "law",
        "events": "event",
        "intrigue": "intrigue",
        "concessions": "concession",
        "senators": "senator",
        "statesmen": "statesman",
        "board": "board",
    }
    prefix = _COMP_TYPE_TO_PREFIX.get(comp_type)
    return f"{prefix}-{slug}" if prefix else slug


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
    for comp_type, components in db.get("components", {}).items():
        if not isinstance(components, dict):
            continue
        for slug, component in components.items():
            if not isinstance(component, dict):
                continue
            item_id = _component_id(comp_type, slug)
            ids.append(item_id)
            texts.append(_component_search_text(component) or component.get("name", slug))

    return ids, texts


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


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


def load_embeddings(
    emb_path: Path,
) -> tuple[list[str], "np.ndarray"] | tuple[None, None]:
    """Load embeddings from *emb_path*.

    Returns (ids, vectors) on success, (None, None) if the file is missing or
    numpy / fastembed is unavailable.
    """
    try:
        import numpy as np
    except ImportError:
        return None, None

    emb_path = Path(emb_path)
    if not emb_path.exists():
        return None, None

    data = np.load(str(emb_path), allow_pickle=False)
    ids: list[str] = data["ids"].tolist()
    vectors: "np.ndarray" = data["vectors"]
    return ids, vectors


def semantic_scores(
    query: str,
    ids: list[str],
    vectors: "np.ndarray",
) -> dict[str, float]:
    """Embed *query* and return cosine-similarity scores keyed by item ID.

    Returns an empty dict if fastembed or numpy is unavailable.
    """
    try:
        import numpy as np
        from fastembed import TextEmbedding
    except ImportError:
        return {}

    model = TextEmbedding("BAAI/bge-small-en-v1.5")
    q_vec = np.array(list(model.embed([query])), dtype=np.float32)[0]

    # Cosine similarity: dot(v, q) / (||v|| * ||q||)
    norms = np.linalg.norm(vectors, axis=1)
    q_norm = float(np.linalg.norm(q_vec))
    if q_norm == 0:
        return {}

    # Avoid division by zero for zero-norm rows
    safe_norms = np.where(norms == 0, 1.0, norms)
    sims = vectors.dot(q_vec) / (safe_norms * q_norm)

    return {item_id: float(sim) for item_id, sim in zip(ids, sims)}
