"""
HuggingFace datasets loader for ERH empirical validation.

Loads ethics_commonsense, social_i_qa, moral_stories.
Maps text embeddings to interaction matrix J_ij via sentence-transformers.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import numpy as np

_HF_AVAILABLE = False
_ST_AVAILABLE = False
try:
    from datasets import load_dataset
    _HF_AVAILABLE = True
except ImportError:
    load_dataset = None

try:
    from sentence_transformers import SentenceTransformer
    _ST_AVAILABLE = True
except ImportError:
    SentenceTransformer = None


def _stub_texts(n: int = 10, seed: int = 42) -> List[str]:
    """Return stub texts when HF/ST unavailable."""
    rng = np.random.default_rng(seed)
    templates = [
        "The person helped the elderly cross the street.",
        "The action caused harm to others.",
        "Lying to protect someone from danger.",
        "Stealing food to feed a hungry child.",
    ]
    return [templates[rng.integers(0, len(templates))] for _ in range(n)]


def load_ethics_commonsense(
    split: str = "train",
    max_samples: Optional[int] = 100,
) -> List[Dict[str, Any]]:
    """Load ethics_commonsense dataset. Returns stub if unavailable."""
    if not _HF_AVAILABLE or load_dataset is None:
        return [{"input": t, "label": 0} for t in _stub_texts(max_samples or 20)]
    try:
        ds = load_dataset("daltonfd/ethics_commonsense", split=split, trust_remote_code=True)
        if max_samples:
            ds = ds.select(range(min(max_samples, len(ds))))
        return [{"input": row.get("input", str(row)), "label": row.get("label", 0)} for row in ds]
    except Exception:
        return [{"input": t, "label": 0} for t in _stub_texts(max_samples or 20)]


def load_social_i_qa(
    split: str = "train",
    max_samples: Optional[int] = 100,
) -> List[Dict[str, Any]]:
    """Load social_i_qa dataset. Returns stub if unavailable."""
    if not _HF_AVAILABLE or load_dataset is None:
        return [{"context": t, "question": "?", "answer": "A"} for t in _stub_texts(max_samples or 20)]
    try:
        ds = load_dataset("social_i_qa", "social_i_qa", split=split, trust_remote_code=True)
        if max_samples:
            ds = ds.select(range(min(max_samples, len(ds))))
        return [
            {
                "context": row.get("context", ""),
                "question": row.get("question", ""),
                "answer": row.get("answer", ""),
            }
            for row in ds
        ]
    except Exception:
        return [{"context": t, "question": "?", "answer": "A"} for t in _stub_texts(max_samples or 20)]


def load_moral_stories(
    split: str = "train",
    max_samples: Optional[int] = 100,
) -> List[Dict[str, Any]]:
    """Load moral_stories dataset. Returns stub if unavailable."""
    if not _HF_AVAILABLE or load_dataset is None:
        return [{"action": t, "intention": "neutral"} for t in _stub_texts(max_samples or 20)]
    try:
        ds = load_dataset("derek-thomas/moral_stories", split=split, trust_remote_code=True)
        if max_samples:
            ds = ds.select(range(min(max_samples, len(ds))))
        return [
            {
                "action": row.get("action", str(row)),
                "intention": row.get("intention", "neutral"),
            }
            for row in ds
        ]
    except Exception:
        return [{"action": t, "intention": "neutral"} for t in _stub_texts(max_samples or 20)]


def text_to_interaction_matrix(
    texts: List[str],
    model_name: str = "all-MiniLM-L6-v2",
    use_stub: bool = False,
) -> np.ndarray:
    """
    Map texts to J_ij coupling matrix via cosine similarity of embeddings.

    Semantic similarity -> J_ij > 0 (ferromagnetic), dissimilarity -> J_ij < 0.

    Parameters
    ----------
    texts : List[str]
        Text strings (actions, contexts, etc.).
    model_name : str, default='all-MiniLM-L6-v2'
        Sentence transformer model.
    use_stub : bool, default=False
        If True, use random matrix (no API).

    Returns
    -------
    ndarray, shape (n, n)
        Symmetric interaction matrix. Clamped to [-1, 1].
    """
    n = len(texts)
    if n == 0:
        return np.zeros((0, 0))
    if use_stub or not _ST_AVAILABLE or SentenceTransformer is None:
        rng = np.random.default_rng(42)
        J = rng.uniform(-0.5, 0.5, (n, n))
        J = (J + J.T) / 2
        np.fill_diagonal(J, 0)
        return np.clip(J, -1, 1)

    model = SentenceTransformer(model_name)
    emb = model.encode(texts, convert_to_numpy=True)
    # Cosine similarity
    norm = np.linalg.norm(emb, axis=1, keepdims=True)
    norm[norm < 1e-12] = 1.0
    emb_n = emb / norm
    J = np.dot(emb_n, emb_n.T)
    np.fill_diagonal(J, 0)
    return np.clip(J, -1, 1)


def extract_V_from_moral_stories(
    rows: List[Dict[str, Any]],
) -> np.ndarray:
    """
    Map moral_stories intention to V(a) in [-1, 1].

    Simplistic: good -> +1, bad -> -1, neutral -> 0.
    """
    mapping = {"good": 1.0, "bad": -1.0, "neutral": 0.0}
    V = []
    for r in rows:
        intention = str(r.get("intention", "neutral")).lower()
        v = mapping.get(intention, 0.0)
        V.append(v)
    return np.array(V) if V else np.array([0.0])


def load_and_build_J(
    dataset: str = "ethics_commonsense",
    max_samples: int = 50,
) -> Tuple[np.ndarray, Optional[np.ndarray]]:
    """
    Load dataset and build interaction matrix J_ij.

    Returns
    -------
    Tuple[ndarray, ndarray | None]
        (J_ij, V) - V is moral values if available, else None.
    """
    texts: List[str] = []
    V: Optional[np.ndarray] = None
    if dataset == "ethics_commonsense":
        rows = load_ethics_commonsense(max_samples=max_samples)
        texts = [str(r.get("input", "")) for r in rows]
    elif dataset == "social_i_qa":
        rows = load_social_i_qa(max_samples=max_samples)
        texts = [str(r.get("context", "")) + " " + str(r.get("question", "")) for r in rows]
    elif dataset == "moral_stories":
        rows = load_moral_stories(max_samples=max_samples)
        texts = [str(r.get("action", "")) for r in rows]
        V = extract_V_from_moral_stories(rows)
    else:
        texts = _stub_texts(max_samples)
    J = text_to_interaction_matrix(texts, use_stub=not _ST_AVAILABLE)
    return J, V
