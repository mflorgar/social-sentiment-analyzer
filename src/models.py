"""Typed models for posts, comments and sentiment outputs."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class Platform(str, Enum):
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"


class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


class Comment(BaseModel):
    id: str
    text: str
    author: str = ""
    created_at: datetime | None = None
    likes: int = 0


class Post(BaseModel):
    id: str
    platform: Platform
    author: str
    text: str
    created_at: datetime
    likes: int = 0
    shares: int = 0
    reach: int = 0
    comments: list[Comment] = Field(default_factory=list)
    media_type: str = "text"  # text | image | video | carousel
    hashtags: list[str] = Field(default_factory=list)


class CommentSentiment(BaseModel):
    comment_id: str
    sentiment: Sentiment
    score: float = Field(..., ge=-1.0, le=1.0, description="Signed score, -1 to +1")
    keywords: list[str] = Field(default_factory=list)


class PostSentiment(BaseModel):
    post_id: str
    platform: Platform
    overall_sentiment: Sentiment
    overall_score: float = Field(..., ge=-1.0, le=1.0)
    comment_sentiments: list[CommentSentiment] = Field(default_factory=list)
    engagement_score: float = Field(..., ge=0.0)
    top_keywords: list[str] = Field(default_factory=list)


class AnalysisReport(BaseModel):
    run_id: str
    generated_at: datetime
    posts_analyzed: int
    comments_analyzed: int
    post_sentiments: list[PostSentiment]
