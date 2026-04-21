"""FastAPI HTTP layer for the sentiment analyzer."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import FileResponse

from src.analyzer import AnalysisPipeline
from src.dashboard import DashboardBuilder
from src.logging_config import configure_logging, get_logger
from src.models import AnalysisReport, Post

configure_logging()
logger = get_logger("api")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Social Sentiment Analyzer",
        description=(
            "Pipeline for sentiment analysis over Facebook and Instagram posts. "
            "Ingests a batch, classifies comments, aggregates by post, and "
            "renders a standalone HTML dashboard."
        ),
        version="0.1.0",
    )

    pipeline = AnalysisPipeline()
    dashboard_builder = DashboardBuilder()

    @app.get("/health", tags=["system"])
    def health():
        return {"status": "ok"}

    @app.post("/analyze", response_model=AnalysisReport, tags=["analysis"])
    def analyze(posts: list[Post]) -> AnalysisReport:
        logger.info("POST /analyze n=%d", len(posts))
        report = pipeline.analyze(posts)

        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        dashboard_builder.build(report, posts, output_dir / f"dashboard_{report.run_id}.html")

        return report

    @app.get("/dashboard/{run_id}", tags=["analysis"])
    def dashboard(run_id: str):
        path = Path("output") / f"dashboard_{run_id}.html"
        if not path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dashboard for run_id={run_id} not found",
            )
        return FileResponse(path, media_type="text/html")

    return app


app = create_app()
