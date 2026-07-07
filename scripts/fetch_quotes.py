#!/usr/bin/env python3
"""
Bakes real daily price history into data/quotes/{TICKER}.json for every ticker
used by the featured index + the sector presets.

Why this exists: the browser can't call Yahoo/Stooq directly (CORS), and the
free public CORS proxies are unreliable. But GitHub Actions has no CORS
restriction, so we fetch here (server-side) and commit the JSON into the repo.
GitHub Pages then serves those files **same-origin**, so the site loads real
data with zero proxy dependency. A scheduled workflow keeps them fresh.

Run locally: python3 scripts/fetch_quotes.py
In CI: same, then commit data/quotes/*.json.
"""
import json
import os
import ssl
import time
import urllib.request
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "data", "quotes")
RANGE = "2y"
SLEEP = 0.25  # be polite to Yahoo, avoid rate limiting


def collect_tickers():
    tickers = set()
    with open(os.path.join(ROOT, "data", "constituents.json"), encoding="utf-8") as f:
        for c in json.load(f):
            tickers.add(c["ticker"].upper())
    with open(os.path.join(ROOT, "data", "presets.json"), encoding="utf-8") as f:
        for p in json.load(f):
            for t in p["tickers"]:
                tickers.add(t.upper())
    return sorted(tickers)


def fetch_yahoo(ticker):
    url = ("https://query1.finance.yahoo.com/v8/finance/chart/"
           + ticker + "?range=" + RANGE + "&interval=1d")
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    result = payload["chart"]["result"][0]
    ts = result["timestamp"]
    q = result["indicators"]["quote"][0]
    closes_raw, volumes_raw = q["close"], q["volume"]
    dates, closes, volumes = [], [], []
    for t, c, v in zip(ts, closes_raw, volumes_raw):
        if c is None:
            continue
        dates.append(datetime.utcfromtimestamp(t).strftime("%Y-%m-%d"))
        closes.append(round(c, 4))
        volumes.append(int(v or 0))
    return dates, closes, volumes


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    tickers = collect_tickers()
    ok, failed = 0, []
    updated = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for i, ticker in enumerate(tickers, 1):
        try:
            dates, closes, volumes = fetch_yahoo(ticker)
            if len(closes) < 5:
                raise ValueError("too few points")
            out = {"ticker": ticker, "updated": updated,
                   "dates": dates, "closes": closes, "volumes": volumes}
            safe = ticker.replace("/", "-")
            with open(os.path.join(OUT_DIR, safe + ".json"), "w", encoding="utf-8") as f:
                json.dump(out, f, separators=(",", ":"))
            ok += 1
            print(f"[{i}/{len(tickers)}] {ticker}: {len(closes)} bars, last {closes[-1]}")
        except Exception as e:
            failed.append(ticker)
            print(f"[{i}/{len(tickers)}] {ticker}: FAILED ({e})")
        time.sleep(SLEEP)

    # index file so the site knows which tickers have baked data available
    index = {"updated": updated, "range": RANGE,
             "tickers": sorted([t for t in tickers if t not in failed])}
    with open(os.path.join(OUT_DIR, "_index.json"), "w", encoding="utf-8") as f:
        json.dump(index, f, separators=(",", ":"))

    print(f"\nDone: {ok} baked, {len(failed)} failed.")
    if failed:
        print("Failed:", ", ".join(failed))


if __name__ == "__main__":
    main()
