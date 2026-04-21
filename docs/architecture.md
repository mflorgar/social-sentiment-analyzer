# Architecture

## Overview

A batch sentiment analysis pipeline for Facebook and Instagram posts.
It ingests a typed batch, runs each comment through a sentiment
backend (mock / Azure / LLM), aggregates by post, and renders a
stand-alone HTML dashboard with Plotly.

The entire stack defaults to a deterministic mock classifier so the
repo runs without API keys. Real providers (Azure Text Analytics,
Anthropic, OpenAI) are plugged in via env vars and optional
dependencies without changing the public interface.

## Pipeline

```
          ┌─────────────┐     ┌──────────────────┐     ┌────────────────┐
JSON ───▶ │  ingest     │ ──▶ │ SentimentAnalyze │ ──▶ │ AnalysisPipeline│
posts     │ (pydantic)  │     │ (per comment)    │     │ (aggregate)    │
          └─────────────┘     └──────────────────┘     └───────┬────────┘
                                                              │
                                     ┌────────────────────────┴────┐
                                     ▼                             ▼
                            ┌────────────────┐            ┌─────────────────┐
                            │ report.json    │            │ dashboard.html  │
                            │ (typed)        │            │ (Plotly, static)│
                            └────────────────┘            └─────────────────┘
```

## Components

- **`src/models.py`** — pydantic models for `Post`, `Comment`,
  `CommentSentiment`, `PostSentiment`, `AnalysisReport`. Everything the
  rest of the code manipulates is strongly typed.
- **`src/analyzer/sentiment.py`** — `SentimentAnalyzer` with a protocol
  and two backends: `MockSentimentBackend` (default) and an Azure Text
  Analytics adapter. Adding a new backend is a small class.
- **`src/analyzer/pipeline.py`** — orchestrates the batch: for each
  post, classify every comment, aggregate into a post-level sentiment,
  compute weighted engagement and surface top keywords.
- **`src/dashboard.py`** — builds a single-file HTML dashboard with
  Plotly (5 charts + KPI header). Runs 100% client-side, no server.
- **`src/api.py`** — FastAPI wrapper with `POST /analyze` and
  `GET /dashboard/{run_id}` endpoints, plus auto-generated `/docs`.

## Why this split

- The analyzer and the pipeline are **pure**: they take data and return
  typed data. Trivial to test, trivial to compose.
- The dashboard takes the typed report and a pandas DataFrame derived
  from it. Swapping the visualization tool (Dash, Streamlit, a
  notebook) is a drop-in replacement.
- The API is a thin adapter on top of the pipeline. The business logic
  is not coupled to HTTP.

## Metrics

- **Comment sentiment**: one of `positive / negative / neutral / mixed`
  plus a signed score in `[-1, 1]`.
- **Post sentiment**: aggregated from comments. When positive and
  negative counts are close, the post is tagged `mixed`; otherwise it
  follows the average score with a neutral band of `±0.15`.
- **Engagement score**: `likes*1 + shares*3 + comments*5`. Weighted
  to reward deeper engagement over cheap likes.

## Extending it

- Swap to a real LLM: implement a backend in `sentiment.py` that returns
  `(Sentiment, score, keywords)` and register it in `_build_backend`.
- Add more charts: each chart is a method in `DashboardBuilder` that
  returns a `go.Figure`. Append it to the list in `build`.
- Add a new metric: extend `PostSentiment` and compute it in
  `AnalysisPipeline.analyze`.
- Connect to Meta Graph API: write an ingest adapter that yields
  `Post` objects. The pipeline does not care where data comes from.
