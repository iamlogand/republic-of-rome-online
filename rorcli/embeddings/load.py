"""Load semantic embeddings from a numpy .npz file."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np


def load_embeddings(
    emb_path: Path,
) -> tuple[list[str], "np.ndarray"] | tuple[None, None]:
    """Load embeddings from *emb_path*.

    Returns (ids, vectors) on success, (None, None) if the file is missing or
    numpy is unavailable.
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
