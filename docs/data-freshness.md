# Data freshness

GMR shows, on every page, when its data was last updated. Nothing about "how
current is this?" is left to guesswork — each surface reads a real timestamp
that was written the moment the data was fetched.

## Where you see it

| Surface | What it shows |
|---|---|
| **Topbar chip** (always visible) | `Prices Xm ago`, color-coded live/stale/old. Hover for exact times; click to jump to the full breakdown. |
| **Methodology → Data freshness & sources** | A table with one row per feed: source, last-updated time, and refresh cadence. |
| **Updates (news) tab** | A one-line freshness summary under the header. |

### Topbar chip colors
- 🟢 **Fresh** — prices under ~90 minutes old (within a live refresh cycle).
- 🟡 **Stale** — older than that but under ~36 hours (e.g. after the close, or over a weekend).
- 🔴 **Old** — over ~36 hours; the refresh workflow may not have run.

## What each feed means

| Feed | Source | Cadence |
|---|---|---|
| **Prices & technical analytics** | Yahoo Finance / Stooq daily OHLCV | Auto-refreshes every 30 min during US market hours. The daily **closing** bar is captured ~45 min after the close. |
| **Company financials** | SEC EDGAR XBRL company-facts | Refreshed weekly. |
| **Events / news feed** | Curated calendar (earnings, catalysts) | Hand-maintained; the "as of" is the last site build. |
| **Relationship graph** | SEC filings, investor decks, public reporting | Curated; illustrative, not exhaustive. |

## How the timestamps are real (not estimated)

- **Prices** — `data/quotes/_index.json` carries an `updated` field written by
  `scripts/fetch_quotes.py` on every run. The topbar chip and tables read that
  field directly, so it reflects the *actual* last successful price pull, not a
  build-time guess.
- **Financials** — `data/sec/_index.json` now carries an `updated` field written
  by `scripts/fetch_sec.py`.
- **News / graph** — the events calendar is a **curated** feed (hand-maintained,
  not a live wire), so its "as of" is the last site build. This is labeled
  "curated" everywhere it appears; forward-looking earnings dates are deliberately
  **not** used as a fake "updated" time.

## Implementation notes

- `build_static_site.py` bakes a `built` ISO timestamp into `window.GMR_DATA`.
- JS helpers (all inside the app IIFE):
  - `fmtAgo(iso)` / `fmtAbs(iso)` — relative and absolute time formatting.
  - `dataFreshness()` — returns `{prices, financials, relationships, news}` ISO strings.
  - `freshnessLine()` — the one-line summary reused by Updates & Methodology.
  - `freshRow(...)` — one row of the Methodology freshness table.
  - `updateDataFreshness()` — refreshes the topbar chip; called on load, after each
    index fetch, and on a 60-second interval.
- The quotes and SEC indexes are fetched at `init()`; each fetch re-runs
  `updateDataFreshness()` so the chip fills in as soon as the data lands.

## Future option

The news/events feed is curated rather than live. Wiring a free RSS/news fetch
into a scheduled workflow would make it stream automatically — a separate
build-out, not yet done.
