"""API tests using FastAPI TestClient."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src.api import create_app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return TestClient(create_app())


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_analyze_returns_report(client, sample_posts):
    payload = [p.model_dump(mode="json") for p in sample_posts]
    resp = client.post("/analyze", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["posts_analyzed"] == 2
    assert data["comments_analyzed"] == 5


def test_dashboard_endpoint_returns_404_when_missing(client):
    resp = client.get("/dashboard/does-not-exist")
    assert resp.status_code == 404
