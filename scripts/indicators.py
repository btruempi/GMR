"""
Indicator math shared by maybe_send_email.py. Mirrors the JavaScript
implementation inlined into index.html by build_static_site.py — keep
the two in sync if you change either. All functions take/return plain
lists aligned to the input length, with None during the warm-up window.
"""


def sma(series, n):
    out = [None] * len(series)
    for i in range(len(series)):
        if i + 1 >= n:
            out[i] = sum(series[i - n + 1:i + 1]) / n
    return out


def ema(series, n):
    out = [None] * len(series)
    k = 2 / (n + 1)
    prev = None
    for i in range(len(series)):
        if prev is None:
            if i + 1 == n:
                prev = sum(series[i - n + 1:i + 1]) / n
                out[i] = prev
            continue
        prev = series[i] * k + prev * (1 - k)
        out[i] = prev
    return out


def rsi(series, n=14):
    out = [None] * len(series)
    if len(series) < n + 1:
        return out
    gains, losses = [], []
    for i in range(1, n + 1):
        change = series[i] - series[i - 1]
        gains.append(max(change, 0))
        losses.append(max(-change, 0))
    avg_gain = sum(gains) / n
    avg_loss = sum(losses) / n
    out[n] = 100 if avg_loss == 0 else 100 - (100 / (1 + avg_gain / avg_loss))
    for i in range(n + 1, len(series)):
        change = series[i] - series[i - 1]
        gain, loss = max(change, 0), max(-change, 0)
        avg_gain = (avg_gain * (n - 1) + gain) / n
        avg_loss = (avg_loss * (n - 1) + loss) / n
        out[i] = 100 if avg_loss == 0 else 100 - (100 / (1 + avg_gain / avg_loss))
    return out


def bollinger(series, n=20, k=2):
    mid = sma(series, n)
    upper, lower = [None] * len(series), [None] * len(series)
    for i in range(len(series)):
        if mid[i] is not None:
            window = series[i - n + 1:i + 1]
            variance = sum((x - mid[i]) ** 2 for x in window) / n
            sd = variance ** 0.5
            upper[i] = mid[i] + k * sd
            lower[i] = mid[i] - k * sd
    return mid, upper, lower


def macd(series, fast=12, slow=26, signal=9):
    ema_fast, ema_slow = ema(series, fast), ema(series, slow)
    line = [None] * len(series)
    for i in range(len(series)):
        if ema_fast[i] is not None and ema_slow[i] is not None:
            line[i] = ema_fast[i] - ema_slow[i]
    signal_line, hist = [None] * len(series), [None] * len(series)
    first = next((i for i, v in enumerate(line) if v is not None), None)
    if first is not None:
        sub_signal = ema(line[first:], signal)
        for j, v in enumerate(sub_signal):
            if v is not None:
                signal_line[first + j] = v
                hist[first + j] = line[first + j] - v
    return line, signal_line, hist


def vwap(closes, volumes):
    out = [None] * len(closes)
    cum_pv = cum_v = 0
    for i in range(len(closes)):
        cum_pv += closes[i] * volumes[i]
        cum_v += volumes[i]
        out[i] = (cum_pv / cum_v) if cum_v else None
    return out


def obv(closes, volumes):
    out = [0] * len(closes)
    for i in range(1, len(closes)):
        if closes[i] > closes[i - 1]:
            out[i] = out[i - 1] + volumes[i]
        elif closes[i] < closes[i - 1]:
            out[i] = out[i - 1] - volumes[i]
        else:
            out[i] = out[i - 1]
    return out


def _atr_proxy(series, n=14):
    changes = [None] + [abs(series[i] - series[i - 1]) for i in range(1, len(series))]
    out = [None] * len(series)
    for i in range(len(series)):
        window = [c for c in changes[max(0, i - n + 1):i + 1] if c is not None]
        if len(window) >= n:
            out[i] = sum(window) / len(window)
    return out


def _money_flow_multiplier(close, prev_close, atr):
    """Synthetic Close-Location-Value proxy: since we have no daily
    high/low, anchor the day's range on the *previous* close (+/- atr/2)
    and see where today's close falls in it. Using today's close to both
    build and locate the range would always collapse to zero."""
    if not atr or atr <= 0 or prev_close is None:
        return None
    mfm = 2 * (close - prev_close) / atr
    return max(-1, min(1, mfm))


def cmf(closes, volumes, n=21):
    atr = _atr_proxy(closes, 14)
    mfv = [None] * len(closes)
    for i in range(1, len(closes)):
        mfm = _money_flow_multiplier(closes[i], closes[i - 1], atr[i])
        if mfm is not None:
            mfv[i] = mfm * volumes[i]
    out = [None] * len(closes)
    for i in range(len(closes)):
        lo = max(0, i - n + 1)
        window_mfv = [mfv[j] for j in range(lo, i + 1) if mfv[j] is not None]
        window_vol = [volumes[j] for j in range(lo, i + 1) if mfv[j] is not None]
        if len(window_mfv) >= n and sum(window_vol) > 0:
            out[i] = sum(window_mfv) / sum(window_vol)
    return out


def mfi(closes, volumes, n=14):
    raw_mf = [closes[i] * volumes[i] for i in range(len(closes))]
    pos, neg = [0] * len(closes), [0] * len(closes)
    for i in range(1, len(closes)):
        if closes[i] > closes[i - 1]:
            pos[i] = raw_mf[i]
        elif closes[i] < closes[i - 1]:
            neg[i] = raw_mf[i]
    out = [None] * len(closes)
    for i in range(len(closes)):
        if i + 1 >= n + 1:
            pos_sum = sum(pos[i - n + 1:i + 1])
            neg_sum = sum(neg[i - n + 1:i + 1])
            out[i] = 100 if neg_sum == 0 else 100 - (100 / (1 + pos_sum / neg_sum))
    return out


def ad_line(closes, volumes):
    atr = _atr_proxy(closes, 14)
    out = [0] * len(closes)
    cum = 0
    for i in range(1, len(closes)):
        mfm = _money_flow_multiplier(closes[i], closes[i - 1], atr[i])
        if mfm is not None:
            cum += mfm * volumes[i]
        out[i] = cum
    return out


def obv_new_high(obv_series, n):
    """True if the latest OBV value is a new N-period high."""
    window = [v for v in obv_series[-n:] if v is not None]
    if len(window) < 2:
        return False
    return window[-1] >= max(window)


def money_flow_status(cmf_series, lookback=21):
    vals = [v for v in cmf_series[-lookback:] if v is not None]
    if not vals:
        return {"label": "Neutral", "cmf": 0, "cls": ""}
    avg = sum(vals) / len(vals)
    if avg >= 0.05:
        return {"label": "Accumulating", "cmf": avg, "cls": "up"}
    if avg <= -0.05:
        return {"label": "Distributing", "cmf": avg, "cls": "down"}
    return {"label": "Neutral", "cmf": avg, "cls": ""}
