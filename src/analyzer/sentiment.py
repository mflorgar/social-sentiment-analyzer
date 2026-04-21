"""Sentiment analysis with a mock fallback and pluggable real backends.

By default the analyzer uses a deterministic keyword-based mock so the
repo runs end-to-end without any API key. Real backends (Azure Text
Analytics, Anthropic, OpenAI) are plugged in via env vars and optional
dependencies without changing the public interface.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Protocol

from src.models import CommentSentiment, Sentiment


class SentimentBackend(Protocol):
    def classify(self, text: str) -> tuple[Sentiment, float, list[str]]: ...


# ---- Mock backend ------------------------------------------------------

_POSITIVE_WORDS = {
    "bueno", "buena", "encanta", "maravilla", "precioso", "preciosos",
    "increíble", "excelente", "perfecto", "gracias", "felicitaciones",
    "arte", "belleza", "aesthetic", "emoción", "emociona", "sí",
    "confío", "guste", "gusto", "mejor", "mejora",
}
_NEGATIVE_WORDS = {
    "caro", "caros", "no", "nunca", "problema", "problemas", "retraso",
    "inaceptable", "cambiaré", "mismos", "falso", "mal", "mala",
    "demasiado",
}


@dataclass
class MockSentimentBackend:
    """Keyword-based mock classifier. Deterministic and zero-dependency."""

    def classify(self, text: str) -> tuple[Sentiment, float, list[str]]:
        tokens = {t.strip(",.¡!¿?").lower() for t in text.split()}
        pos = len(tokens & _POSITIVE_WORDS)
        neg = len(tokens & _NEGATIVE_WORDS)

        if pos == 0 and neg == 0:
            return Sentiment.NEUTRAL, 0.0, []
        if pos > 0 and neg > 0:
            score = (pos - neg) / (pos + neg)
            sentiment = Sentiment.MIXED
        elif pos > neg:
            score = min(1.0, pos / 3)
            sentiment = Sentiment.POSITIVE
        else:
            score = -min(1.0, neg / 3)
            sentiment = Sentiment.NEGATIVE

        keywords = sorted(tokens & (_POSITIVE_WORDS | _NEGATIVE_WORDS))[:5]
        return sentiment, score, keywords


# ---- Real backend adapters --------------------------------------------

def _azure_backend() -> SentimentBackend:
    try:
        from azure.ai.textanalytics import TextAnalyticsClient  # type: ignore
        from azure.core.credentials import AzureKeyCredential   # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "azure-ai-textanalytics no está instalado. "
            "Añádelo a requirements y reinstala."
        ) from exc

    endpoint = os.environ["AZURE_LANGUAGE_ENDPOINT"]
    key = os.environ["AZURE_LANGUAGE_KEY"]
    client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    _MAP = {
        "positive": Sentiment.POSITIVE,
        "negative": Sentiment.NEGATIVE,
        "neutral": Sentiment.NEUTRAL,
        "mixed": Sentiment.MIXED,
    }

    class _Backend:
        def classify(self, text: str) -> tuple[Sentiment, float, list[str]]:
            resp = client.analyze_sentiment(documents=[text])[0]
            sentiment = _MAP.get(resp.sentiment, Sentiment.NEUTRAL)
            # Signed score: positive minus negative confidence
            conf = resp.confidence_scores
            score = round(conf.positive - conf.negative, 3)
            return sentiment, score, []

    return _Backend()


# ---- Facade ------------------------------------------------------------

class SentimentAnalyzer:
    """Public API. Resolves provider from env var at construction."""

    def __init__(self, provider: str | None = None) -> None:
        self.provider = (provider or os.getenv("SENTIMENT_PROVIDER", "mock")).lower()
        self._backend: SentimentBackend = self._build_backend()

    def _build_backend(self) -> SentimentBackend:
        if self.provider == "azure":
            return _azure_backend()
        return MockSentimentBackend()

    def analyze_comment(self, comment_id: str, text: str) -> CommentSentiment:
        sentiment, score, keywords = self._backend.classify(text)
        return CommentSentiment(
            comment_id=comment_id,
            sentiment=sentiment,
            score=score,
            keywords=keywords,
        )
