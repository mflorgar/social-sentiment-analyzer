"""Orchestrates ingest → classify → aggregate → report."""

from __future__ import annotations

import uuid
from collections import Counter
from datetime import datetime

from src.logging_config import get_logger
from src.models import (
    AnalysisReport,
    CommentSentiment,
    Post,
    PostSentiment,
    Sentiment,
)

from .sentiment import SentimentAnalyzer

logger = get_logger("analyzer.pipeline")


def _aggregate_sentiment(comment_sentiments: list[CommentSentiment]) -> tuple[Sentiment, float]:
    """Roll up comment-level sentiments into a single post-level verdict."""
    if not comment_sentiments:
        return Sentiment.NEUTRAL, 0.0

    avg_score = round(
        sum(cs.score for cs in comment_sentiments) / len(comment_sentiments), 3
    )

    counts = Counter(cs.sentiment for cs in comment_sentiments)
    pos, neg = counts[Sentiment.POSITIVE], counts[Sentiment.NEGATIVE]

    if pos > 0 and neg > 0 and abs(pos - neg) <= 1:
        overall = Sentiment.MIXED
    elif avg_score > 0.15:
        overall = Sentiment.POSITIVE
    elif avg_score < -0.15:
        overall = Sentiment.NEGATIVE
    else:
        overall = Sentiment.NEUTRAL

    return overall, avg_score


def _engagement_score(post: Post) -> float:
    """Weighted engagement: comments weigh more than shares, shares more than likes."""
    return round(
        (post.likes * 1.0)
        + (post.shares * 3.0)
        + (len(post.comments) * 5.0),
        2,
    )


class AnalysisPipeline:
    """Analyzes a batch of posts and returns a typed report."""

    def __init__(self, analyzer: SentimentAnalyzer | None = None) -> None:
        self.analyzer = analyzer or SentimentAnalyzer()

    def analyze(self, posts: list[Post]) -> AnalysisReport:
        logger.info("pipeline: analyzing %d posts", len(posts))
        post_sentiments: list[PostSentiment] = []
        total_comments = 0

        for post in posts:
            comment_sents = [
                self.analyzer.analyze_comment(c.id, c.text) for c in post.comments
            ]
            total_comments += len(comment_sents)
            overall, avg = _aggregate_sentiment(comment_sents)

            keywords = Counter()
            for cs in comment_sents:
                keywords.update(cs.keywords)
            top_keywords = [k for k, _ in keywords.most_common(5)]

            post_sentiments.append(PostSentiment(
                post_id=post.id,
                platform=post.platform,
                overall_sentiment=overall,
                overall_score=avg,
                comment_sentiments=comment_sents,
                engagement_score=_engagement_score(post),
                top_keywords=top_keywords,
            ))
            logger.info(
                "  %s (%s): %s (score=%s, engagement=%s)",
                post.id, post.platform.value, overall.value, avg,
                post_sentiments[-1].engagement_score,
            )

        return AnalysisReport(
            run_id=str(uuid.uuid4()),
            generated_at=datetime.utcnow(),
            posts_analyzed=len(posts),
            comments_analyzed=total_comments,
            post_sentiments=post_sentiments,
        )
