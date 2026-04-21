"""Shared fixtures."""

from __future__ import annotations

from datetime import datetime

import pytest

from src.models import Comment, Platform, Post


@pytest.fixture
def sample_posts() -> list[Post]:
    return [
        Post(
            id="fb_test",
            platform=Platform.FACEBOOK,
            author="TestBrand",
            text="Announcement",
            created_at=datetime(2026, 4, 1, 10, 0, 0),
            likes=100, shares=10, reach=1000,
            comments=[
                Comment(id="c1", text="Me encanta, es precioso"),
                Comment(id="c2", text="Demasiado caros, inaceptable"),
                Comment(id="c3", text="Gracias por el aviso"),
            ],
        ),
        Post(
            id="ig_test",
            platform=Platform.INSTAGRAM,
            author="TestBrand",
            text="New drop",
            created_at=datetime(2026, 4, 2, 11, 0, 0),
            likes=200, shares=0, reach=2000,
            comments=[
                Comment(id="c4", text="Increíble diseño, felicitaciones"),
                Comment(id="c5", text="Qué aesthetic, me encanta"),
            ],
        ),
    ]
