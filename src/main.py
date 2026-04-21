"""CLI demo: ingest sample posts, analyze, render dashboard."""

from __future__ import annotations

import json
from pathlib import Path

from dotenv import load_dotenv

from src.analyzer import AnalysisPipeline
from src.dashboard import DashboardBuilder
from src.logging_config import configure_logging, get_logger
from src.models import Post


logger = get_logger("main")


DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "sample_posts.json"


def load_posts(path: Path = DATA_FILE) -> list[Post]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [Post.model_validate(item) for item in raw]


def main() -> None:
    load_dotenv()
    configure_logging()

    posts = load_posts()
    logger.info("loaded %d posts from %s", len(posts), DATA_FILE.name)

    pipeline = AnalysisPipeline()
    report = pipeline.analyze(posts)

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    # Save report JSON
    report_path = output_dir / "report.json"
    report_path.write_text(report.model_dump_json(indent=2), encoding="utf-8")

    # Build dashboard HTML
    dashboard_path = output_dir / "dashboard.html"
    DashboardBuilder().build(report, posts, dashboard_path)

    logger.info("done → %s · %s", report_path, dashboard_path)


if __name__ == "__main__":
    main()
