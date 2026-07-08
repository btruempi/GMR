#!/usr/bin/env python3
"""
Bakes real "where the money comes from and goes" data from SEC filings into
data/sec/{TICKER}.json for every tracked ticker.

Source of truth: the SEC's free XBRL company-facts API (data.sec.gov), which
exposes the numbers companies report in their 10-K/20-F/40-F filings. We extract
the latest fiscal-year money-IN (revenue) and money-OUT allocations (cost of
revenue, R&D, SG&A, capex, taxes, interest, dividends, buybacks) plus net
income. The Knowledge Graph tab renders these as a node-edge money-flow.

SEC asks for a descriptive User-Agent and <10 requests/sec. Run:
    python3 scripts/fetch_sec.py
"""
import json
import os
import ssl
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "data", "sec")
UA = "Growth Markets Research (personal research; bentruempi2@gmail.com)"
SLEEP = 0.2  # stay well under SEC's rate limit

# concept -> list of candidate XBRL tags (first that resolves wins)
CONCEPTS = {
    "revenue": ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues",
                "RevenueFromContractWithCustomerIncludingAssessedTax", "SalesRevenueNet"],
    "cogs": ["CostOfRevenue", "CostOfGoodsAndServicesSold", "CostOfGoodsSold"],
    "rnd": ["ResearchAndDevelopmentExpense"],
    "sga": ["SellingGeneralAndAdministrativeExpense", "GeneralAndAdministrativeExpense"],
    "capex": ["PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets"],
    "taxes": ["IncomeTaxExpenseBenefit"],
    "interest": ["InterestExpense", "InterestAndDebtExpense"],
    "dividends": ["PaymentsOfDividendsCommonStock", "PaymentsOfDividends"],
    "buybacks": ["PaymentsForRepurchaseOfCommonStock"],
    "netIncome": ["NetIncomeLoss", "ProfitLoss"],
}
ANNUAL_FORMS = ("10-K", "10-K/A", "20-F", "40-F", "20-F/A", "40-F/A")


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "gzip, deflate"})
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=25, context=ctx) as resp:
        raw = resp.read()
        if resp.headers.get("Content-Encoding") == "gzip":
            import gzip
            raw = gzip.decompress(raw)
        return json.loads(raw.decode("utf-8"))


def load_cik_map():
    data = _get("https://www.sec.gov/files/company_tickers.json")
    return {v["ticker"].upper(): (str(v["cik_str"]).zfill(10), v.get("title", "")) for v in data.values()}


def latest_annual(facts, tags):
    """Most-recent fiscal-year value across ALL candidate tags (companies switch
    XBRL tags over time, so pick the globally latest end date, not the first tag
    that happens to have any data). Returns (val, end, fy)."""
    best = None
    for taxonomy in ("us-gaap", "ifrs-full"):
        g = facts.get(taxonomy, {})
        for tag in tags:
            node = g.get(tag)
            if not node:
                continue
            for unit, vals in node.get("units", {}).items():
                if not unit.startswith("USD"):
                    continue
                for v in vals:
                    if v.get("form") not in ANNUAL_FORMS or v.get("fp") != "FY":
                        continue
                    if v.get("val") is None:
                        continue
                    if best is None or v["end"] > best["end"]:
                        best = v
    if best is not None:
        return best["val"], best["end"], best.get("fy")
    return None, None, None


def build_ticker(ticker, cik, title):
    facts = _get("https://data.sec.gov/api/xbrl/companyfacts/CIK" + cik + ".json").get("facts", {})
    out = {"ticker": ticker, "cik": cik, "name": title or ticker, "fy": None, "in": {}, "out": {}, "net": None}
    fy_end = None
    for key, tags in CONCEPTS.items():
        val, end, fy = latest_annual(facts, tags)
        if val is None:
            continue
        if end and (fy_end is None or end > fy_end):
            fy_end = end
        if key == "revenue":
            out["in"]["revenue"] = val
        elif key == "netIncome":
            out["net"] = val
        else:
            out["out"][key] = val
    out["fy"] = fy_end
    if not out["in"].get("revenue"):
        raise ValueError("no revenue reported (likely a foreign/limited filer)")
    return out


def collect_tickers():
    def _load(p, d):
        path = os.path.join(ROOT, p)
        try:
            return json.load(open(path, encoding="utf-8")) if os.path.exists(path) else d
        except Exception:
            return d
    tickers = set(c["ticker"].upper() for c in _load("data/constituents.json", []))
    for p in _load("data/presets.json", []):
        for t in p.get("tickers", []):
            tickers.add(t.upper())
    for t in _load("data/extra_tickers.json", []):
        tickers.add(str(t).upper())
    return sorted(tickers)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print("[GMR] Loading SEC ticker->CIK map...")
    cikmap = load_cik_map()
    tickers = collect_tickers()
    ok, failed = 0, []
    for i, t in enumerate(tickers, 1):
        entry = cikmap.get(t)
        if not entry:
            failed.append(t + "(no CIK)")
            print(f"[{i}/{len(tickers)}] {t}: no CIK")
            continue
        cik, title = entry
        try:
            out = build_ticker(t, cik, title)
            with open(os.path.join(OUT_DIR, t.replace("/", "-") + ".json"), "w", encoding="utf-8") as f:
                json.dump(out, f, separators=(",", ":"))
            ok += 1
            rev = out["in"]["revenue"]
            print(f"[{i}/{len(tickers)}] {t}: rev {rev/1e9:.1f}B, FY {out['fy']}")
        except Exception as e:
            failed.append(t)
            print(f"[{i}/{len(tickers)}] {t}: FAILED ({e})")
        time.sleep(SLEEP)

    index = {"tickers": sorted([t for t in tickers if os.path.exists(os.path.join(OUT_DIR, t.replace('/','-') + '.json'))])}
    with open(os.path.join(OUT_DIR, "_index.json"), "w", encoding="utf-8") as f:
        json.dump(index, f, separators=(",", ":"))
    print(f"\n[GMR] SEC data: {ok} baked, {len(failed)} without usable data.")


if __name__ == "__main__":
    main()
