#!/usr/bin/env python3
"""
Runs inside .github/workflows/nri-email.yml on two schedules:
  - */15 13-20 * * 1-5  -> evaluate alert rules, send an email for any newly
                           triggered rule.
  - 0 8 * * *           -> maybe send a digest, gated by data/email_settings.json
                           cadence (daily/weekly/monthly/quarterly/yearly/off).
Also runs on workflow_dispatch, either as a manual alert check or -- with
NRI_TEST_MODE=1 -- a synthetic test alert that bypasses every condition, used
by the "Send me a test alert NOW" button on the Alerts tab.

Everything here is pure standard library (urllib, smtplib, json) so it needs
no pip installs in the Actions runner.
"""
import json
import os
import smtplib
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from email.mime.text import MIMEText

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import indicators as ind

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_json(rel_path, default=None):
    path = os.path.join(ROOT, rel_path)
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(rel_path, data):
    path = os.path.join(ROOT, rel_path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def synthetic_series(ticker, days=260):
    """Deterministic seeded random walk -- mirrors the JS syntheticSeries so
    the offline fallback looks like a believable chart, not a sine wave."""
    import random
    seed = sum((i + 1) * ord(c) for i, c in enumerate(ticker))
    rng = random.Random(seed)
    price = 20 + (seed % 180)
    drift = (rng.random() - 0.45) * 0.0012
    vol = 0.012 + rng.random() * 0.02
    dates, closes, volumes = [], [], []
    base_vol = 400000 + (seed % 9) * 300000
    for i in range(days):
        shock = (rng.random() + rng.random() + rng.random() - 1.5) * vol
        if rng.random() > 0.97:
            shock *= 3
        price = max(1.0, price * (1 + drift + shock))
        dates.append(f"synthetic-{i}")
        closes.append(round(price, 2))
        volumes.append(int(base_vol * (0.6 + rng.random() * 1.6)))
    return {"dates": dates, "closes": closes, "volumes": volumes, "synthetic": True}


def fetch_series(ticker):
    """Baked quotes first (data/quotes/{TICKER}.json, refreshed by the
    refresh-quotes workflow), then live Yahoo, then Stooq, then a synthetic
    series if everything fails (gotcha #5: log clearly and keep going rather
    than crashing the whole run)."""
    baked_path = os.path.join(ROOT, "data", "quotes", ticker.upper() + ".json")
    if os.path.exists(baked_path):
        try:
            with open(baked_path, encoding="utf-8") as f:
                j = json.load(f)
            if len(j.get("closes", [])) >= 5:
                return {"dates": j["dates"], "closes": j["closes"],
                        "volumes": j["volumes"], "synthetic": False}
        except Exception as e:
            print(f"[GMR] Baked quote read failed for {ticker}: {e}")

    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range=1y&interval=1d"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        result = payload["chart"]["result"][0]
        ts = result["timestamp"]
        closes_raw = result["indicators"]["quote"][0]["close"]
        volumes_raw = result["indicators"]["quote"][0]["volume"]
        dates, closes, volumes = [], [], []
        for t, c, v in zip(ts, closes_raw, volumes_raw):
            if c is None:
                continue
            dates.append(datetime.utcfromtimestamp(t).strftime("%Y-%m-%d"))
            closes.append(c)
            volumes.append(v or 0)
        if len(closes) >= 5:
            return {"dates": dates, "closes": closes, "volumes": volumes, "synthetic": False}
    except Exception as e:
        print(f"[GMR] Yahoo fetch failed for {ticker}: {e}")

    stooq_url = f"https://stooq.com/q/d/l/?s={ticker.lower()}.us&i=d"
    try:
        req = urllib.request.Request(stooq_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            text = resp.read().decode("utf-8")
        lines = text.strip().split("\n")[1:]
        dates, closes, volumes = [], [], []
        for line in lines:
            parts = line.split(",")
            if len(parts) < 6:
                continue
            try:
                closes.append(float(parts[4]))
            except ValueError:
                continue
            dates.append(parts[0])
            try:
                volumes.append(float(parts[5]))
            except ValueError:
                volumes.append(0)
        if len(closes) >= 5:
            return {"dates": dates, "closes": closes, "volumes": volumes, "synthetic": False}
    except Exception as e:
        print(f"[GMR] Stooq fetch failed for {ticker}: {e}")

    print(f"[GMR] Both sources failed for {ticker}, using a synthetic series so the run keeps going.")
    return synthetic_series(ticker)


def evaluate_rule(rule, series):
    """Returns (triggered: bool, detail: str)."""
    closes, volumes, dates = series["closes"], series["volumes"], series["dates"]
    if len(closes) < 5:
        return False, "insufficient data"
    p = rule.get("params", {})
    t = rule["type"]
    last = closes[-1]

    if t == "price_above":
        return last > p["price"], f"price {last:.2f} > {p['price']}"
    if t == "price_below":
        return last < p["price"], f"price {last:.2f} < {p['price']}"
    if t == "pct_change":
        n = int(p.get("days", 5))
        if len(closes) <= n:
            return False, "insufficient history"
        change = (last / closes[-1 - n] - 1) * 100
        return abs(change) >= abs(p["pct"]), f"{n}d change {change:.1f}%"
    if t == "pct_change_from_anchor":
        anchor = p.get("anchor")
        idx = next((i for i, d in enumerate(dates) if d >= anchor), None) if anchor else None
        if idx is None:
            return False, "anchor date not in range"
        change = (last / closes[idx] - 1) * 100
        return abs(change) >= abs(p["pct"]), f"change since {anchor}: {change:.1f}%"
    if t in ("rsi_above", "rsi_below"):
        rsi = ind.rsi(closes, 14)
        val = rsi[-1]
        if val is None:
            return False, "RSI not available yet"
        ok = val > p["level"] if t == "rsi_above" else val < p["level"]
        return ok, f"RSI {val:.1f}"
    if t in ("sma_cross_up", "sma_cross_down"):
        fast, slow = ind.sma(closes, 50), ind.sma(closes, 200)
        if fast[-1] is None or slow[-1] is None or fast[-2] is None or slow[-2] is None:
            return False, "SMA not available yet"
        was_below = fast[-2] <= slow[-2]
        now_above = fast[-1] > slow[-1]
        if t == "sma_cross_up":
            return was_below and now_above, f"SMA50 {fast[-1]:.2f} vs SMA200 {slow[-1]:.2f}"
        was_above = fast[-2] >= slow[-2]
        now_below = fast[-1] < slow[-1]
        return was_above and now_below, f"SMA50 {fast[-1]:.2f} vs SMA200 {slow[-1]:.2f}"
    if t in ("macd_cross_up", "macd_cross_down"):
        line, signal, _ = ind.macd(closes)
        if line[-1] is None or signal[-1] is None or line[-2] is None or signal[-2] is None:
            return False, "MACD not available yet"
        if t == "macd_cross_up":
            return line[-2] <= signal[-2] and line[-1] > signal[-1], f"MACD {line[-1]:.2f} vs signal {signal[-1]:.2f}"
        return line[-2] >= signal[-2] and line[-1] < signal[-1], f"MACD {line[-1]:.2f} vs signal {signal[-1]:.2f}"
    if t == "volume_spike":
        if len(volumes) < 21:
            return False, "insufficient history"
        avg20 = sum(volumes[-21:-1]) / 20
        mult = p.get("multiplier", 2)
        return (volumes[-1] >= mult * avg20 if avg20 else False), f"vol {volumes[-1]:.0f} vs {mult}x avg {avg20:.0f}"
    if t in ("money_pouring_in", "distribution_warning"):
        cmf = ind.cmf(closes, volumes, 21)
        val = cmf[-1]
        if val is None:
            return False, "CMF not available yet"
        threshold = p.get("threshold", 0.05)
        if t == "money_pouring_in":
            return val >= threshold, f"CMF {val:.3f}"
        return val <= -threshold, f"CMF {val:.3f}"
    if t in ("mfi_overbought", "mfi_oversold"):
        mfi = ind.mfi(closes, volumes, 14)
        val = mfi[-1]
        if val is None:
            return False, "MFI not available yet"
        ok = val > p["level"] if t == "mfi_overbought" else val < p["level"]
        return ok, f"MFI {val:.1f}"
    if t == "obv_breakout":
        obv = ind.obv(closes, volumes)
        lookback = int(p.get("lookback", 20))
        return ind.obv_new_high(obv, lookback), "OBV new high"

    return False, f"unknown rule type {t}"


def send_email(to_addr, cc_addrs, subject, body):
    """Sends via Gmail SMTP. The SENDER is the Gmail account that owns the
    GMAIL_APP_PASSWORD: set GMAIL_USER to that address to send to any recipient;
    if GMAIL_USER is unset we assume the recipient itself is the Gmail account
    (the common 'alert myself' case)."""
    password = os.environ.get("GMAIL_APP_PASSWORD")
    sender = (os.environ.get("GMAIL_USER") or to_addr or "").strip()
    if not password or not sender:
        print(f"[GMR] Skipping send (missing GMAIL_APP_PASSWORD or sender/recipient). Subject was: {subject}")
        return False
    recipients = [r for r in ([to_addr] + [c for c in (cc_addrs or []) if c]) if r]
    if not recipients:
        recipients = [sender]
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to_addr or sender
    cc = [c for c in (cc_addrs or []) if c]
    if cc:
        msg["Cc"] = ", ".join(cc)
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=20) as server:
            server.login(sender, password)
            server.sendmail(sender, recipients, msg.as_string())
        print(f"[GMR] Sent '{subject}' from {sender} to {', '.join(recipients)}")
        return True
    except Exception as e:
        print(f"[GMR] Email send FAILED: {e} -- check the Gmail address and that "
              f"GMAIL_APP_PASSWORD is a 16-char App Password (not your login password), with 2FA enabled.")
        return False


def sms_gateway_address(channels):
    sms = channels.get("sms") or {}
    number, carrier = sms.get("number"), sms.get("carrier")
    if number and carrier:
        return f"{number}@{carrier}"
    return None


def send_ntfy(title, body):
    """Free push notification via ntfy.sh -- no account, no personal email.
    Set repo secret NTFY_TOPIC to a hard-to-guess topic (or a full URL); install
    the ntfy app and subscribe to that topic to get push alerts on your phone."""
    topic = (os.environ.get("NTFY_TOPIC") or "").strip()
    if not topic:
        return False
    url = topic if topic.startswith("http") else ("https://ntfy.sh/" + topic)
    try:
        req = urllib.request.Request(
            url, data=body.encode("utf-8"),
            headers={"Title": title.encode("ascii", "ignore").decode(), "Tags": "chart_with_upwards_trend"})
        urllib.request.urlopen(req, timeout=15)
        print(f"[GMR] Sent ntfy push -> {url}")
        return True
    except Exception as e:
        print(f"[GMR] ntfy push failed: {e}")
        return False


def send_discord(title, body):
    """Free alert into a Discord channel via an incoming webhook URL (repo secret
    DISCORD_WEBHOOK). No personal email involved."""
    webhook = (os.environ.get("DISCORD_WEBHOOK") or "").strip()
    if not webhook:
        return False
    payload = json.dumps({"content": f"**{title}**\n{body}"[:1900]}).encode("utf-8")
    try:
        req = urllib.request.Request(webhook, data=payload, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=15)
        print("[GMR] Sent Discord message")
        return True
    except Exception as e:
        print(f"[GMR] Discord send failed: {e}")
        return False


def notify(channels, subject, body):
    """Deliver an alert over every configured channel. ntfy + Discord need no
    personal email; email/SMS are optional."""
    sent = False
    to_addr = channels.get("email")
    if to_addr:
        sent = send_email(to_addr, [sms_gateway_address(channels)], subject, body) or sent
    sent = send_ntfy(subject, body) or sent
    sent = send_discord(subject, body) or sent
    if not sent:
        print(f"[GMR] No channel delivered '{subject}'. Configure NTFY_TOPIC (free push), "
              f"DISCORD_WEBHOOK, or GMAIL_APP_PASSWORD.")
    return sent


def run_test_alert(channels):
    notify(
        channels,
        "GMR test alert -- your pipeline works",
        "This is a synthetic test alert from Growth Markets Research. "
        "If you got this, your workflow and notification channels are wired up correctly.",
    )


def run_alert_check():
    alerts = load_json("data/alerts.json", {"channels": {}, "rules": []})
    state = load_json("data/alerts_state.json", {})
    channels = alerts.get("channels", {})
    rules = [r for r in alerts.get("rules", []) if r.get("enabled", True)]

    series_cache = {}
    fired = []
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    for rule in rules:
        ticker = rule["ticker"]
        if ticker not in series_cache:
            series_cache[ticker] = fetch_series(ticker)
        series = series_cache[ticker]
        triggered, detail = evaluate_rule(rule, series)

        rule_key = rule["id"]
        prev = state.get(rule_key, {"last_triggered": False, "last_fired_ts": None})
        # Edge-triggered: only fire on the false->true transition, so the same
        # rule can re-arm later the same day if price crosses back and forth
        # (dedup key carries a full timestamp, not just a date -- gotcha #9).
        if triggered and not prev["last_triggered"]:
            fired.append((rule, detail))
            state[rule_key] = {"last_triggered": True, "last_fired_ts": now_iso}
        else:
            state[rule_key] = {"last_triggered": triggered, "last_fired_ts": prev["last_fired_ts"]}

    save_json("data/alerts_state.json", state)

    if not fired:
        print("[GMR] No new alert triggers this run.")
        return

    lines = [f"- {r['ticker']}: {r['type']} ({detail})" for r, detail in fired]
    body = "Growth Markets Research -- alerts triggered:\n\n" + "\n".join(lines)
    notify(channels, f"GMR: {len(fired)} alert(s) triggered", body)


CADENCE_DAYS = {"weekly": 0, "monthly": 1, "quarterly": 1, "yearly": 1}  # Monday=0 for weekly


def digest_due_today(cadence):
    today = datetime.now(timezone.utc)
    if cadence == "off" or not cadence:
        return False
    if cadence == "daily":
        return True
    if cadence == "weekly":
        return today.weekday() == 0
    if cadence == "monthly":
        return today.day == 1
    if cadence == "quarterly":
        return today.day == 1 and today.month in (1, 4, 7, 10)
    if cadence == "yearly":
        return today.day == 1 and today.month == 1
    return False


def run_digest():
    settings = load_json("data/email_settings.json", {"cadence": "off", "email": ""})
    cadence = settings.get("cadence", "off")
    if not digest_due_today(cadence):
        print(f"[GMR] Digest cadence is '{cadence}', not due today.")
        return

    constituents = load_json("data/constituents.json", [])
    lines = []
    for c in constituents:
        series = fetch_series(c["ticker"])
        closes = series["closes"]
        chg = (closes[-1] / closes[-2] - 1) * 100 if len(closes) > 1 else 0
        lines.append(f"- {c['ticker']} ({c['name']}): {closes[-1]:.2f} ({chg:+.1f}% today)")

    body = f"Growth Markets Research -- {cadence} digest\n\n" + "\n".join(lines)
    alerts = load_json("data/alerts.json", {"channels": {}})
    channels = dict(alerts.get("channels", {}))
    if settings.get("email"):
        channels["email"] = settings["email"]
    notify(channels, f"GMR {cadence} digest", body)


def main():
    if os.environ.get("NRI_TEST_MODE") == "1":
        alerts = load_json("data/alerts.json", {"channels": {}})
        run_test_alert(alerts.get("channels", {}))
        return

    trigger_cron = os.environ.get("NRI_TRIGGER_CRON", "")
    if trigger_cron == "0 8 * * *":
        run_digest()
    else:
        run_alert_check()


if __name__ == "__main__":
    main()
