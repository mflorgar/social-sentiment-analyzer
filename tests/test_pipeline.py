"""Tests for the full analysis pipeline."""

from __future__ import annotations

from src.analyzer import AnalysisPipeline
from src.models import Sentiment


def test_pipeline_returns_report_with_correct_counts(sample_posts):
    report = AnalysisPipeline().analyze(sample_posts)
    assert report.posts_analyzed == 2
    assert report.comments_analyzed == 5
    assert len(report.post_sentiments) == 2


def test_post_sentiment_has_engagement_score(sample_posts):
    report = AnalysisPipeline().analyze(sample_posts)
    for ps in report.post_sentiments:
        assert ps.engagement_score > 0


def test_positive_post_is_classified_positive(sample_posts):
    report = AnalysisPipeline().analyze(sample_posts)
    ig_post = next(ps for ps in report.post_sentiments if ps.post_id == "ig_test")
    assert ig_post.overall_sentiment == Sentiment.POSITIVE


def test_empty_input_returns_empty_report():
    report = AnalysisPipeline().analyze([])
    assert report.posts_analyzed == 0
    assert report.comments_analyzed == 0
    assert report.post_sentiments == []
