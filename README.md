# Social Sentiment Analyzer

![CI](https://github.com/mflorgar/social-sentiment-analyzer/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

Batch pipeline that ingests Facebook and Instagram posts with their
comments, classifies sentiment per comment, aggregates into a
post-level verdict, and renders a stand-alone HTML dashboard with
Plotly.

The whole stack runs out of the box with a deterministic mock
classifier, so you can clone and demo without any API key. Real
providers (Azure Text Analytics, Anthropic, OpenAI) plug in via
environment variables without touching the core code.

## 👀 Live preview

Want to see the dashboard **without installing anything**? There is a
static preview with mock data deployed on Vercel:

**Live demo**: https://social-sentiment-demo.vercel.app *(update with real URL after deploy)*

The demo lives in the [`demo/`](demo/) folder of this same repo. It is
a single self-contained HTML file with Plotly from CDN, so Vercel
serves it without any build step. See [`demo/README.md`](demo/README.md)
for how to deploy your own copy.

Use the **Regenerar datos** button to re-roll the mock data and
**Escenario** to cycle between positive, negative and balanced datasets.

## Why this repo

Reference architecture for the kind of project I delivered at EY:
ingesting social-media signals, analyzing sentiment with Azure
Cognitive Services, and feeding real-time dashboards for the Marketing
team. This repo strips that down to a minimal, testable shape.

## Stack

- Python 3.10+, pydantic for typed models
- Plotly for the self-contained HTML dashboard
- pandas for aggregations
- FastAPI for the REST layer, with auto-generated OpenAPI docs
- Optional: Azure Text Analytics, Anthropic, OpenAI
- **12 tests** (unit + integration + API) and GitHub Actions CI

## Architecture

```
          ┌─────────┐    ┌──────────────────┐    ┌────────────────┐
JSON ───▶ │ ingest  │──▶ │ SentimentAnalyze │──▶ │ AnalysisPipeline│──┐
posts     │         │    │ (per comment)    │    │ (aggregate)    │  │
          └─────────┘    └──────────────────┘    └────────────────┘  │
                                                                      ▼
                                 ┌──────────────┐     ┌────────────────────┐
                                 │ report.json  │◀────│ dashboard.html     │
                                 │ (typed)      │     │ (Plotly, static)   │
                                 └──────────────┘     └────────────────────┘
```

Full design notes in [`docs/architecture.md`](docs/architecture.md).

## Quick start

```bash
git clone https://github.com/mflorgar/social-sentiment-analyzer.git
cd social-sentiment-analyzer
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m src.main
```

Expected output:

```
loaded 5 posts from sample_posts.json
pipeline: analyzing 5 posts
  fb_001 (facebook): positive (score=0.25, engagement=1521.0)
  ig_001 (instagram): mixed (score=0.111, engagement=3435.0)
  fb_002 (facebook): mixed (score=-0.167, engagement=101.0)
  ig_002 (instagram): neutral (score=0.083, engagement=5690.0)
  fb_003 (facebook): positive (score=0.667, engagement=1525.0)
dashboard: wrote output/dashboard.html
```

A pre-generated dashboard is committed to
[`examples/dashboard.html`](examples/dashboard.html) so you can
open it in a browser without running anything.

## Dashboard

The generated HTML includes:

- KPI header (posts, comments, % positive, % negative, avg engagement)
- Comment-sentiment distribution (donut)
- Engagement vs sentiment score (scatter, bubble size = reach)
- Sentiment by platform (stacked bars)
- Top keywords detected in comments (horizontal bars)

All charts are Plotly, interactive, and embedded via CDN. No server
needed, open the HTML file directly.

## Run as REST API

```bash
uvicorn src.api:app --reload
```

- `POST /analyze` — receive a batch of posts, return an `AnalysisReport`
- `GET /dashboard/{run_id}` — serve the generated dashboard HTML
- `GET /docs` — interactive Swagger UI
- `GET /health`

## Tests

```bash
pytest
```

12 tests covering: mock sentiment classifier (positive / negative /
neutral / mixed), pipeline aggregations, post-level scoring, dashboard
generation, and API endpoints.

## Plugging in real backends

```env
SENTIMENT_PROVIDER=azure
AZURE_LANGUAGE_ENDPOINT=https://yourresource.cognitiveservices.azure.com
AZURE_LANGUAGE_KEY=...
```

Uncomment the optional dependencies in `requirements.txt`. The
pipeline signature doesn't change; only the backend implementation
does.

## Project layout

```
social-sentiment-analyzer/
├── src/
│   ├── analyzer/         # SentimentAnalyzer + AnalysisPipeline
│   ├── dashboard.py      # Plotly HTML builder
│   ├── api.py            # FastAPI layer
│   ├── models.py         # pydantic models
│   ├── logging_config.py
│   └── main.py           # CLI demo
├── data/
│   └── sample_posts.json # 5 realistic FB+IG posts with comments
├── tests/                # 12 tests
├── docs/
│   └── architecture.md
├── examples/
│   ├── dashboard.html    # Pre-generated dashboard
│   └── report.json       # Pre-generated typed report
├── .github/workflows/ci.yml
├── .env.example
├── requirements.txt
└── README.md
```

## Roadmap

- [ ] Ingest adapters: Meta Graph API, CSV export, Google BigQuery
- [ ] Per-language sentiment (detect language first, pick a specialized model)
- [ ] Topic modeling on comments (clusters of themes)
- [ ] Incremental mode: persist previous runs and show deltas
- [ ] Alert thresholds (e.g. flag posts with > 30% negative comments)

## License

MIT - see [LICENSE](LICENSE).

---

Built by [Maria Flores](https://github.com/mflorgar).
