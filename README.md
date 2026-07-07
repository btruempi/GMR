# Growth Markets Research (GMR)

**Spot growth before it moves.** A personal, zero-cost research platform for
finding high-growth opportunities in growing markets — named watchlists across
30+ sectors, technical **and** money-flow charting, portfolio optimization,
backtesting, and rule-based email/SMS alerts that fire during market hours.

Everything runs on free tiers. No signup beyond Gmail + GitHub, no API keys, no
paid data feeds, no backend server. Total ongoing cost: **$0/month** on a public
repo.

---

## What's inside

A single static `index.html` (deployable to GitHub Pages) plus a lightweight
Python + GitHub Actions backend for scheduled alerts.

| Tab | What it does |
|-----|--------------|
| **Dashboard** | Featured composite index chart, sector doughnut, quick actions. |
| **Watchlists** | The main workflow. Named baskets, one-click clones of 30+ sector presets, per-list indicator toggles, a table with quotes + RSI + MFI + a money-flow status column, and click-to-expand charts with a linked oscillator pane. |
| **Companies** | Look up any US-listed ticker (live from Yahoo/Stooq), full chart + key metrics, and a compare-multiple-stocks card. |
| **Optimizer** | Max-Sharpe / min-vol / equal-weight / inverse-vol portfolios at 15/20/25% position caps, with a **clickable** efficient frontier. |
| **Backtest** | Composite vs SPY / URA / NLR, lookback 1Y–Max, rolling drawdown + rolling 63-day Sharpe overlays. |
| **Updates** | Merged catalyst calendar + news feed with type + ticker filters. |
| **Pre-IPO** | Private-company watchlist with status tags. |
| **Profile** | Risk-profile form plus a plain-English quick command bar (no LLM — pure pattern matching). |
| **Alerts** | 16 rule types incl. money-flow rules (CMF / MFI / OBV), quick-recipe chips, email + SMS-gateway channels, one-click "Arm my alerts," a live test alert, and a red/green setup diagnostic. |
| **Methodology** | List-aware selector, editable tiered constituent weights, and the email-digest schedule + "turn on scheduled emails" control. |

### Indicators (implemented identically in JS and Python)

SMA, EMA, RSI-14 (Wilder), Bollinger 20/2, MACD 12/26/9, VWAP, volume bars,
**OBV**, **CMF-21** (Chaikin Money Flow), **MFI-14** (Money Flow Index), and the
**A/D line**. Indicators that traditionally need daily high/low use a synthetic
14-day ATR proxy so they work from close-and-volume data alone.

---

## Quick start

```bash
bash deploy.sh
```

The script is idempotent and handles: Xcode Command Line Tools, `git init` + remote,
the macOS Python SSL-cert fix, the rebuild, and the commit/push. At the end it
prints your live GitHub Pages URL and the three remaining manual steps.

### Turning on email alerts (one-time)

1. On the site, open **Methodology → Email digest schedule**, paste your Gmail
   address and a GitHub Personal Access Token, and click **Turn on scheduled
   emails**. This commits the workflow + Python scripts into your repo via the
   GitHub API.
2. Add a repository secret named **`GMAIL_APP_PASSWORD`** (a
   [Gmail App Password](https://myaccount.google.com/apppasswords)) under
   *Settings → Secrets and variables → Actions*.
3. On the **Alerts** tab, click **Send me a test alert NOW** — you should get an
   email within about a minute. Use **Diagnose setup** if not.

> **Token scopes:** the "push to GitHub" flows write to
> `.github/workflows/nri-email.yml`, so your token needs **both** `repo` **and**
> `workflow` scopes. The setup UI links to a pre-filled token page.

---

## How live data works

Prices come from a three-tier chain, most-reliable first:

1. **Baked, same-origin data (primary).** `scripts/fetch_quotes.py` runs in
   GitHub Actions (`refresh-quotes.yml`, every 30 min during market hours),
   fetches ~2y of daily history for every constituent + preset ticker via
   `urllib` (no CORS server-side), and commits `data/quotes/{TICKER}.json`.
   GitHub Pages serves those files from **your own origin**, so the site loads
   real prices with **zero proxy dependency** — this is what makes it reliable.
2. **Live CORS proxies (fallback).** For arbitrary tickers you search on the
   Companies tab (not in the baked set), the browser tries a rotating chain of
   public CORS proxies wrapping Yahoo/Stooq, with `localStorage` health
   tracking. Free proxies are flaky, so this is best-effort only.
3. **Synthetic series (last resort).** A deterministic seeded random walk so
   nothing ever renders blank if both above fail.

Chart.js is inlined at build time, so the UI works offline. The server-side
alert script (`maybe_send_email.py`) reads the same baked `data/quotes/*.json`
first, so alerts evaluate against identical data with no network call.

> The baked snapshot is as fresh as the last `refresh-quotes` run (every 30 min
> in market hours). Run `python3 scripts/fetch_quotes.py` locally + rebuild to
> refresh on demand.

---

## Project layout

```
GMR/
├── README.md                     # this file
├── build_static_site.py          # generates index.html from data/ + vendor/
├── deploy.sh                     # one-shot deploy to GitHub Pages
├── data/                         # hand-curated seed JSON (constituents, presets, …)
├── scripts/
│   ├── indicators.py             # indicator math (mirror of the inlined JS)
│   └── maybe_send_email.py       # alert evaluator + digest sender (stdlib only)
├── .github/workflows/
│   └── nri-email.yml             # */15 market-hours cron + daily digest + test dispatch
├── vendor/chart.umd.min.js       # inlined into index.html at build time
├── .nojekyll                     # tell Pages to serve the HTML as-is
├── index.html                    # built artifact — commit this
└── Nuclear-Renaissance-Index.html# legacy filename (identical copy)
```

Rebuild any time with `python3 build_static_site.py`.

---

## Constraints (by design)

- **No LLM calls anywhere.** The natural-language command bar is pure JS pattern
  matching.
- **No paid data feeds** — Stooq + Yahoo only.
- **No backend server** — only GitHub Actions.
- **$0/month** on public repos.

---

## Disclaimer

The preset lists and featured index are hand-curated **starting points**, not
investment advice. Prices are best-effort and can lag or fall back to synthetic
data. Email-to-SMS gateways are unreliable; for guaranteed SMS, Twilio is a
natural (paid) upgrade path that is intentionally not implemented here to keep
the tool free. Do your own research.
