"""Compute cosine-similarity scores between a query and stored embeddings."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np


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
