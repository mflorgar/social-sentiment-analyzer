"""Tests for the SentimentAnalyzer mock backend."""

from __future__ import annotations

from src.analyzer import SentimentAnalyzer
from src.models import Sentiment


def test_positive_comment():
    cs = SentimentAnalyzer(provider="mock").analyze_comment(
        "c", "Me encanta, es precioso, felicitaciones"
    )
    assert cs.sentiment == Sentiment.POSITIVE
    assert cs.score > 0
    assert "encanta" in cs.keywords


def test_negative_comment():
    cs = SentimentAnalyzer(provider="mock").analyze_comment(
        "c", "Demasiado caros, es inaceptable y con problemas"
    )
    assert cs.sentiment == Sentiment.NEGATIVE
    assert cs.score < 0


def test_neutral_comment():
    cs = SentimentAnalyzer(provider="mock").analyze_comment(
        "c", "Recibí el pedido hoy"
    )
    assert cs.sentiment == Sentiment.NEUTRAL
    assert cs.score == 0.0


def test_mixed_comment():
    cs = SentimentAnalyzer(provider="mock").analyze_comment(
        "c", "Me encanta pero demasiado caros"
    )
    assert cs.sentiment == Sentiment.MIXED
