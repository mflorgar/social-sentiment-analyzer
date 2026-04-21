"""Tests for the HTML dashboard builder."""

from __future__ import annotations

from pathlib import Path

from src.analyzer import AnalysisPipeline
from src.dashboard import DashboardBuilder


def test_dashboard_generates_html_file(sample_posts, tmp_path):
    report = AnalysisPipeline().analyze(sample_posts)
    path = DashboardBuilder().build(report, sample_posts, tmp_path / "dash.html")

    assert path.exists()
    content = path.read_text(encoding="utf-8")
    assert "Social Sentiment Dashboard" in content
    assert "plotly" in content.lower()  # Plotly was embedded
