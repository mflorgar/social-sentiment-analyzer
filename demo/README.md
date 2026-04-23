# Demo — static dashboard preview

Single-file HTML dashboard with **mock data** that mirrors what the
Python pipeline produces. Useful for showing the visual output without
running the analyzer.

- `index.html` — self-contained, pulls Plotly from CDN. Open directly in
  a browser, or serve from `python3 -m http.server`.
- No build, no dependencies, no backend.

## Deploy on Vercel

This folder is set up to be deployed **on its own**, without touching
the Python code in the parent repo.

On [vercel.com/new](https://vercel.com/new), when importing the repo:

1. **Framework Preset**: `Other`
2. **Root Directory**: `demo` ← important, otherwise Vercel will try to
   build the Python project
3. **Build Command**: leave empty
4. **Output Directory**: leave empty (Vercel serves the root of `demo`)
5. Deploy.

Vercel will publish `demo/index.html` as the site root.

## Scenarios

The demo cycles through three scenarios (positive-leaning,
negative-leaning, balanced) via the *Escenario* button. The *Regenerar
datos* button re-rolls the random seed keeping the same scenario.
