"""
HuggingFace Ethical Oracle for action scoring.

Uses pre-trained models (e.g., unitary/toxic-bert) to score action text
as a proxy for ethical value V(a). Maps toxicity to V: less toxic = more ethical.
"""

import hashlib
import json
import logging
from pathlib import Path
from typing import Optional

try:
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    _TRANSFORMERS_AVAILABLE = True
except ImportError:
    _TRANSFORMERS_AVAILABLE = False
    AutoModelForSequenceClassification = None
    AutoTokenizer = None


class HuggingFaceEthicalOracle:
    """
    Use a pre-trained model (e.g., unitary/toxic-bert) to score action text.

    Toxicity score 0.0-1.0 is mapped to V in [-1, 1] via:
    V = 2 * (1 - toxicity) - 1  (less toxic = more ethical).

    Supports JSON cache to avoid re-downloading and re-inferencing the same text.
    """

    def __init__(
        self,
        model_name: str = "unitary/toxic-bert",
        cache_path: Optional[str] = None,
        use_sentiment_model: bool = False,
    ):
        """
        Parameters
        ----------
        model_name : str, default='unitary/toxic-bert'
            HuggingFace model for toxicity or sentiment.
        cache_path : str or None, default=None
            Path to JSON cache file. If None, no cache is used.
        use_sentiment_model : bool, default=False
            If True, use sentiment model (positive=ethical). Else use toxicity (1-tox=ethical).
        """
        self.model_name = model_name
        self.cache_path = Path(cache_path) if cache_path else None
        self.use_sentiment_model = use_sentiment_model
        self._model = None
        self._tokenizer = None
        self._cache: dict[str, float] = {}
        if self.cache_path and self.cache_path.exists():
            try:
                with open(self.cache_path, encoding="utf-8") as f:
                    self._cache = json.load(f)
            except Exception:
                self._cache = {}

    def _load_model(self) -> None:
        """Lazy load model and tokenizer on first score() call."""
        if self._model is not None:
            return
        if not _TRANSFORMERS_AVAILABLE:
            return
        try:
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self._model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            self._model.eval()
        except Exception as e:
            logging.warning("HuggingFaceEthicalOracle: failed to load model %s: %s", self.model_name, e)

    def _to_V(self, score: float) -> float:
        """
        Map model score to V in [-1, 1].

        For toxicity: V = 2 * (1 - toxicity) - 1
        For sentiment: V = 2 * (pos_score) - 1
        """
        if self.use_sentiment_model:
            return max(-1.0, min(1.0, 2.0 * score - 1.0))
        return max(-1.0, min(1.0, 2.0 * (1.0 - score) - 1.0))

    def score(self, action_text: str) -> float:
        """
        Score action text and return V in [-1, 1].

        Parameters
        ----------
        action_text : str
            Text description of the action (e.g., from action_to_scenario_text).

        Returns
        -------
        float
            Ethical value V in [-1, 1]. Returns 0.0 if transformers unavailable.
        """
        if not action_text or not str(action_text).strip():
            return 0.0

        key = hashlib.sha256(action_text.encode("utf-8")).hexdigest()
        if key in self._cache:
            return self._cache[key]

        if not _TRANSFORMERS_AVAILABLE:
            logging.warning("HuggingFaceEthicalOracle: transformers not installed, returning 0.0")
            return 0.0

        self._load_model()
        if self._model is None or self._tokenizer is None:
            return 0.0

        try:
            import torch

            inputs = self._tokenizer(
                action_text[:512],
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True,
            )
            with torch.no_grad():
                outputs = self._model(**inputs)
                logits = outputs.logits
                if logits.shape[-1] == 1:
                    prob = torch.sigmoid(logits).item()
                elif self.use_sentiment_model:
                    probs = torch.softmax(logits, dim=-1)
                    prob = probs[0][2].item() if probs.shape[-1] > 2 else probs[0][1].item()
                else:
                    # Toxicity heads like unitary/toxic-bert are MULTI-LABEL:
                    # each label needs its own sigmoid. Softmax across labels
                    # dilutes strong signals and index [1] is "severe_toxic",
                    # so toxic text used to score as safe. Prefer the "toxic"
                    # label when present, else the strongest label.
                    probs = torch.sigmoid(logits)[0]
                    id2label = getattr(self._model.config, "id2label", None) or {}
                    toxic_idx = next(
                        (int(i) for i, name in id2label.items() if str(name).lower() == "toxic"),
                        None,
                    )
                    prob = probs[toxic_idx].item() if toxic_idx is not None else probs.max().item()
            v = self._to_V(float(prob))
            self._cache[key] = v
            if self.cache_path:
                self.cache_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.cache_path, "w", encoding="utf-8") as f:
                    json.dump(self._cache, f, indent=0)
            return v
        except MemoryError:
            # VUL-011: Differentiate fatal errors from transient ones.
            logging.error(
                "HuggingFaceEthicalOracle: out of memory during inference for model %s. "
                "Consider reducing batch size or using a smaller model.",
                self.model_name,
            )
            return 0.0
        except RuntimeError as e:
            # GPU/CUDA or tensor dimension errors — likely non-transient.
            logging.error(
                "HuggingFaceEthicalOracle: RuntimeError during inference (model=%s): %s. "
                "Returning fallback value 0.0.",
                self.model_name,
                e,
            )
            return 0.0
        except Exception as e:
            # Transient or unknown errors — log with context for debugging.
            logging.warning(
                "HuggingFaceEthicalOracle: inference failed (model=%s): %s. "
                "Returning fallback value 0.0. "
                "Note: this value is indistinguishable from a neutral ethical score.",
                self.model_name,
                e,
            )
            return 0.0
