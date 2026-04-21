"""Self-contained HTML dashboard built with Plotly.

Compact, neutral-palette layout: KPI header on top, 4 charts in a
2-column grid underneath. The dashboard is a single HTML file, no
server required.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.logging_config import get_logger
from src.models import AnalysisReport, Post

logger = get_logger("dashboard")


# Neutral palette: muted, comfortable on the eye, professional look.
PALETTE = {
    "positive": "#7BA69F",  # sage
    "negative": "#C8856D",  # terracotta
    "neutral":  "#9CA3AF",  # warm gray
    "mixed":    "#C9A89A",  # beige
}
ACCENT = "#5B6B5B"
MUTED_TEXT = "#6B6B6B"
GRID_COLOR = "#ECECE9"


_PLOTLY_BASE_LAYOUT = dict(
    font=dict(family="Helvetica, Arial, sans-serif", size=11, color="#2A2A2A"),
    margin=dict(l=40, r=20, t=40, b=40),
    paper_bgcolor="white",
    plot_bgcolor="white",
    title=dict(font=dict(size=13, color="#2A2A2A"), x=0.02, xanchor="left"),
    legend=dict(
        font=dict(size=10),
        bgcolor="rgba(0,0,0,0)",
        orientation="h",
        y=-0.2,
    ),
    xaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
    yaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
)


def _apply_style(fig: go.Figure, height: int = 280) -> go.Figure:
    fig.update_layout(**_PLOTLY_BASE_LAYOUT, height=height)
    return fig


class DashboardBuilder:
    """Builds a compact, neutral-styled HTML dashboard."""

    def build(self, report: AnalysisReport, posts: list[Post], output_path: str | Path) -> Path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        df_posts = self._posts_df(report, posts)
        df_comments = self._comments_df(report)

        kpis = self._compute_kpis(df_posts, df_comments)
        charts = [
            self._sentiment_distribution(df_comments),
            self._sentiment_by_platform(df_comments),
            self._engagement_vs_sentiment(df_posts),
            self._top_keywords(df_comments),
        ]

        self._write_html(output_path, kpis, charts, report)
        logger.info("dashboard: wrote %s", output_path)
        return output_path

    # ---- DataFrame helpers ------------------------------------------

    def _posts_df(self, report: AnalysisReport, posts: list[Post]) -> pd.DataFrame:
        post_lookup = {p.id: p for p in posts}
        rows = []
        for ps in report.post_sentiments:
            p = post_lookup[ps.post_id]
            rows.append({
                "post_id": ps.post_id,
                "platform": ps.platform.value,
                "author": p.author,
                "text": p.text[:60] + ("…" if len(p.text) > 60 else ""),
                "sentiment": ps.overall_sentiment.value,
                "score": ps.overall_score,
                "engagement": ps.engagement_score,
                "likes": p.likes,
                "shares": p.shares,
                "comments": len(p.comments),
                "reach": p.reach,
            })
        return pd.DataFrame(rows)

    def _comments_df(self, report: AnalysisReport) -> pd.DataFrame:
        rows = []
        for ps in report.post_sentiments:
            for cs in ps.comment_sentiments:
                rows.append({
                    "post_id": ps.post_id,
                    "platform": ps.platform.value,
                    "comment_id": cs.comment_id,
                    "sentiment": cs.sentiment.value,
                    "score": cs.score,
                    "keywords": cs.keywords,
                })
        return pd.DataFrame(rows)

    # ---- KPIs --------------------------------------------------------

    def _compute_kpis(self, df_posts: pd.DataFrame, df_comments: pd.DataFrame) -> list[dict]:
        total_posts = len(df_posts)
        total_comments = len(df_comments)
        if not df_comments.empty:
            positive_pct = round((df_comments["sentiment"] == "positive").mean() * 100, 1)
            negative_pct = round((df_comments["sentiment"] == "negative").mean() * 100, 1)
        else:
            positive_pct = negative_pct = 0
        avg_engagement = round(df_posts["engagement"].mean(), 0) if not df_posts.empty else 0
        return [
            {"label": "Posts", "value": total_posts, "suffix": "", "color": ACCENT},
            {"label": "Comments", "value": total_comments, "suffix": "", "color": ACCENT},
            {"label": "Positive", "value": positive_pct, "suffix": "%", "color": PALETTE["positive"]},
            {"label": "Negative", "value": negative_pct, "suffix": "%", "color": PALETTE["negative"]},
            {"label": "Avg engagement", "value": int(avg_engagement), "suffix": "", "color": ACCENT},
        ]

    # ---- Charts ------------------------------------------------------

    def _sentiment_distribution(self, df_comments: pd.DataFrame) -> go.Figure:
        counts = df_comments["sentiment"].value_counts().reset_index()
        counts.columns = ["sentiment", "count"]
        fig = px.pie(
            counts, names="sentiment", values="count",
            color="sentiment", color_discrete_map=PALETTE,
            hole=0.55,
        )
        fig.update_layout(title_text="Comment sentiment")
        fig.update_traces(
            textinfo="percent+label",
            textfont_size=11,
            marker=dict(line=dict(color="white", width=2)),
        )
        return _apply_style(fig)

    def _sentiment_by_platform(self, df_comments: pd.DataFrame) -> go.Figure:
        pivot = (
            df_comments.groupby(["platform", "sentiment"])
            .size()
            .reset_index(name="count")
        )
        fig = px.bar(
            pivot, x="platform", y="count", color="sentiment",
            color_discrete_map=PALETTE, barmode="stack",
        )
        fig.update_layout(title_text="Sentiment by platform")
        fig.update_yaxes(title_text="Comments")
        fig.update_xaxes(title_text="")
        return _apply_style(fig)

    def _engagement_vs_sentiment(self, df_posts: pd.DataFrame) -> go.Figure:
        fig = px.scatter(
            df_posts,
            x="score", y="engagement",
            color="sentiment", size="reach",
            size_max=30,
            hover_data=["post_id", "platform", "author", "text"],
            color_discrete_map=PALETTE,
        )
        fig.update_layout(title_text="Engagement vs sentiment score")
        fig.update_xaxes(title_text="Sentiment score", range=[-1.1, 1.1])
        fig.update_yaxes(title_text="Engagement")
        fig.update_traces(marker=dict(line=dict(width=0.5, color="white")))
        return _apply_style(fig)

    def _top_keywords(self, df_comments: pd.DataFrame) -> go.Figure:
        counter: Counter[str] = Counter()
        for kws in df_comments["keywords"]:
            counter.update(kws)
        most_common = counter.most_common(10)
        if not most_common:
            fig = go.Figure()
            fig.update_layout(title_text="Top keywords (no data)")
            return _apply_style(fig)
        df = pd.DataFrame(most_common, columns=["keyword", "count"])
        fig = px.bar(
            df.sort_values("count"),
            x="count", y="keyword", orientation="h",
        )
        fig.update_layout(title_text="Top keywords")
        fig.update_traces(marker_color=ACCENT)
        fig.update_xaxes(title_text="")
        fig.update_yaxes(title_text="")
        return _apply_style(fig)

    # ---- HTML output -------------------------------------------------

    def _write_html(
        self,
        output_path: Path,
        kpis: list[dict],
        charts: list[go.Figure],
        report: AnalysisReport,
    ) -> None:
        kpi_html = "".join(
            f"<div class='kpi'>"
            f"  <div class='kpi-label'>{k['label']}</div>"
            f"  <div class='kpi-value' style='color:{k['color']}'>"
            f"    {k['value']}<span class='kpi-suffix'>{k['suffix']}</span>"
            f"  </div>"
            f"</div>"
            for k in kpis
        )

        chart_html = "".join(
            "<div class='chart-card'>"
            + fig.to_html(full_html=False, include_plotlyjs="cdn" if i == 0 else False,
                          config={"displaylogo": False, "responsive": True})
            + "</div>"
            for i, fig in enumerate(charts)
        )

        meta = (
            f"Run {report.run_id[:8]} · "
            f"{report.generated_at.isoformat(timespec='seconds')} · "
            f"{report.posts_analyzed} posts, {report.comments_analyzed} comments"
        )

        html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Social Sentiment Dashboard</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  :root {{
    --bg: #FAFAF9;
    --card-bg: #FFFFFF;
    --card-border: #EAEAE7;
    --text: #2A2A2A;
    --muted: {MUTED_TEXT};
    --accent: {ACCENT};
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    padding: 32px 24px;
    font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue",
                 Helvetica, Arial, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.45;
  }}
  .container {{
    max-width: 1080px;
    margin: 0 auto;
  }}
  header {{
    margin-bottom: 24px;
  }}
  h1 {{
    margin: 0 0 4px;
    font-size: 22px;
    font-weight: 600;
    letter-spacing: -0.01em;
  }}
  .meta {{
    color: var(--muted);
    font-size: 12px;
  }}
  .kpi-grid {{
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 12px;
    margin: 20px 0 24px;
  }}
  .kpi {{
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 8px;
    padding: 14px 16px;
  }}
  .kpi-label {{
    font-size: 11px;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 4px;
  }}
  .kpi-value {{
    font-size: 24px;
    font-weight: 600;
  }}
  .kpi-suffix {{
    font-size: 14px;
    font-weight: 500;
    margin-left: 2px;
  }}
  .chart-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
  }}
  .chart-card {{
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 8px;
    padding: 6px;
    overflow: hidden;
  }}
  .chart-card .plotly-graph-div {{ width: 100% !important; }}
  @media (max-width: 760px) {{
    .kpi-grid {{ grid-template-columns: repeat(2, 1fr); }}
    .chart-grid {{ grid-template-columns: 1fr; }}
  }}
  footer {{
    margin-top: 28px;
    font-size: 11px;
    color: var(--muted);
    text-align: center;
  }}
</style>
</head>
<body>
<div class="container">
  <header>
    <h1>Social Sentiment Dashboard</h1>
    <div class="meta">{meta}</div>
  </header>

  <div class="kpi-grid">
    {kpi_html}
  </div>

  <div class="chart-grid">
    {chart_html}
  </div>

  <footer>Generated by social-sentiment-analyzer · Plotly</footer>
</div>
</body>
</html>
"""
        output_path.write_text(html, encoding="utf-8")
