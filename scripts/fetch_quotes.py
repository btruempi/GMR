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
import urllib.parse
import http.cookiejar
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "data", "quotes")
RANGE = "2y"
SLEEP = 0.25  # be polite to Yahoo, avoid rate limiting
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"


def yahoo_session():
    """Yahoo's fundamentals endpoints (v10 quoteSummary) require a cookie + a
    matching crumb. Grab a cookie from fc.yahoo.com, then fetch the crumb.
    Returns (opener, crumb) or (None, None) if the handshake fails."""
    try:
        cj = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(cj),
            urllib.request.HTTPSHandler(context=ssl.create_default_context()))
        opener.addheaders = [("User-Agent", UA)]
        try:
            opener.open("https://fc.yahoo.com", timeout=15)
        except Exception:
            pass  # returns 404 but still sets the cookie
        crumb = opener.open(
            "https://query1.finance.yahoo.com/v1/test/getcrumb", timeout=15
        ).read().decode("utf-8").strip()
        if crumb and "<" not in crumb:
            return opener, crumb
    except Exception as e:
        print(f"[GMR] Crumb handshake failed ({e}); fundamentals will be skipped.")
    return None, None


def _raw(node):
    if isinstance(node, dict):
        return node.get("raw", node.get("fmt"))
    return node


def fetch_fundamentals(opener, crumb, ticker):
    """Returns a flat dict of fundamentals, or {} on any failure."""
    if not opener or not crumb:
        return {}
    modules = "price,summaryDetail,defaultKeyStatistics,assetProfile,financialData,calendarEvents"
    url = ("https://query2.finance.yahoo.com/v10/finance/quoteSummary/"
           + ticker + "?modules=" + modules + "&crumb=" + urllib.parse.quote(crumb))
    try:
        data = json.loads(opener.open(url, timeout=15).read().decode("utf-8"))
        r = data["quoteSummary"]["result"][0]
    except Exception:
        return {}
    sd = r.get("summaryDetail", {}) or {}
    pr = r.get("price", {}) or {}
    ks = r.get("defaultKeyStatistics", {}) or {}
    ap = r.get("assetProfile", {}) or {}
    fd = r.get("financialData", {}) or {}
    ce = r.get("calendarEvents", {}) or {}
    earnings = ((ce.get("earnings") or {}).get("earningsDate") or [])
    earnings_ts = _raw(earnings[0]) if earnings else None
    return {
        "name": pr.get("longName") or pr.get("shortName") or ticker,
        "exchange": pr.get("exchangeName"),
        "currency": pr.get("currency"),
        "marketCap": _raw(pr.get("marketCap")) or _raw(sd.get("marketCap")),
        "previousClose": _raw(sd.get("previousClose")),
        "open": _raw(sd.get("open")),
        "bid": _raw(sd.get("bid")), "ask": _raw(sd.get("ask")),
        "dayLow": _raw(sd.get("dayLow")), "dayHigh": _raw(sd.get("dayHigh")),
        "volume": _raw(sd.get("volume")),
        "avgVolume": _raw(sd.get("averageVolume")),
        "fiftyTwoWeekLow": _raw(sd.get("fiftyTwoWeekLow")),
        "fiftyTwoWeekHigh": _raw(sd.get("fiftyTwoWeekHigh")),
        "beta": _raw(sd.get("beta")) or _raw(ks.get("beta")),
        "trailingPE": _raw(sd.get("trailingPE")),
        "forwardPE": _raw(sd.get("forwardPE")),
        "trailingEps": _raw(ks.get("trailingEps")),
        "forwardEps": _raw(ks.get("forwardEps")),
        "priceToBook": _raw(ks.get("priceToBook")),
        "sharesOutstanding": _raw(ks.get("sharesOutstanding")),
        "dividendRate": _raw(sd.get("dividendRate")),
        "dividendYield": _raw(sd.get("dividendYield")),
        "exDividendDate": _raw(sd.get("exDividendDate")),
        "targetMeanPrice": _raw(fd.get("targetMeanPrice")),
        "earningsDate": earnings_ts,
        "sector": ap.get("sector"),
        "industry": ap.get("industry"),
        "website": ap.get("website"),
        "employees": ap.get("fullTimeEmployees"),
        "summary": (ap.get("longBusinessSummary") or "")[:900],
    }


def _load(rel_path, default):
    path = os.path.join(ROOT, rel_path)
    if not os.path.exists(path):
        return default
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def collect_tickers():
    """Universe = constituents + presets + the user's saved watchlists +
    an editable data/extra_tickers.json. Anything the user adds to a watchlist
    (once pushed via 'Arm my alerts') or drops in extra_tickers.json gets real
    baked data on the next refresh."""
    tickers = set()
    for c in _load("data/constituents.json", []):
        tickers.add(c["ticker"].upper())
    for p in _load("data/presets.json", []):
        for t in p.get("tickers", []):
            tickers.add(t.upper())
    wl = _load("data/watchlists.json", {})
    for lst in (wl.get("lists") or {}).values():
        for t in lst.get("tickers", []):
            tickers.add(t.upper())
    for t in _load("data/extra_tickers.json", []):
        tickers.add(str(t).upper())
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
    o_raw, h_raw, l_raw = q["open"], q["high"], q["low"]
    closes_raw, volumes_raw = q["close"], q["volume"]
    dates, opens, highs, lows, closes, volumes = [], [], [], [], [], []
    for i, t in enumerate(ts):
        c = closes_raw[i]
        if c is None:
            continue
        # fall back to close when an individual OHLC field is missing
        o = o_raw[i] if o_raw[i] is not None else c
        h = h_raw[i] if h_raw[i] is not None else max(o, c)
        lo = l_raw[i] if l_raw[i] is not None else min(o, c)
        dates.append(datetime.utcfromtimestamp(t).strftime("%Y-%m-%d"))
        opens.append(round(o, 4))
        highs.append(round(h, 4))
        lows.append(round(lo, 4))
        closes.append(round(c, 4))
        volumes.append(int(volumes_raw[i] or 0))
    return dates, opens, highs, lows, closes, volumes


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    tickers = collect_tickers()
    ok, failed, fund_ok = 0, [], 0
    updated = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    opener, crumb = yahoo_session()
    print(f"[GMR] Fundamentals session: {'OK' if crumb else 'unavailable (OHLCV only)'}")
    for i, ticker in enumerate(tickers, 1):
        try:
            dates, opens, highs, lows, closes, volumes = fetch_yahoo(ticker)
            if len(closes) < 5:
                raise ValueError("too few points")
            fundamentals = fetch_fundamentals(opener, crumb, ticker)
            if fundamentals:
                fund_ok += 1
            out = {"ticker": ticker, "updated": updated, "dates": dates,
                   "opens": opens, "highs": highs, "lows": lows,
                   "closes": closes, "volumes": volumes,
                   "fundamentals": fundamentals}
            safe = ticker.replace("/", "-")
            with open(os.path.join(OUT_DIR, safe + ".json"), "w", encoding="utf-8") as f:
                json.dump(out, f, separators=(",", ":"))
            ok += 1
            mc = fundamentals.get("marketCap")
            print(f"[{i}/{len(tickers)}] {ticker}: {len(closes)} bars, last {closes[-1]}" + (f", mktcap {mc}" if mc else ""))
        except Exception as e:
            failed.append(ticker)
            print(f"[{i}/{len(tickers)}] {ticker}: FAILED ({e})")
        time.sleep(SLEEP)
    print(f"[GMR] Fundamentals baked for {fund_ok}/{len(tickers)} tickers.")

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
