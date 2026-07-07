#!/usr/bin/env python3
"""
Builds index.html (and a legacy-named copy, Nuclear-Renaissance-Index.html)
for Growth Markets Research from data/*.json + vendor/chart.umd.min.js.

Everything ships as one static HTML file: Chart.js is inlined so the page
works offline, and the seed data is inlined as a JS constant so the first
paint never depends on a network call. Live prices are fetched client-side
at load time via the CORS proxy chain in APP_JS.

Run: python3 build_static_site.py
"""
import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))


def load_json(name):
    with open(os.path.join(ROOT, "data", name), encoding="utf-8") as f:
        return json.load(f)


def load_text(rel_path):
    with open(os.path.join(ROOT, rel_path), encoding="utf-8") as f:
        return f.read()


def build_seed_data():
    return {
        "constituents": load_json("constituents.json"),
        "catalysts": load_json("catalysts.json"),
        "preIpo": load_json("pre_ipo.json"),
        "profile": load_json("profile.json"),
        "emailSettings": load_json("email_settings.json"),
        "alerts": load_json("alerts.json"),
        "watchlists": load_json("watchlists.json"),
        "presets": load_json("presets.json"),
    }


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
CSS = r"""
:root{
  --bg:#0b0f14; --bg2:#111826; --panel:#151d2b; --panel2:#1b2536;
  --border:#26324a; --text:#e7edf7; --muted:#93a2bb; --accent:#4fd1c5;
  --accent2:#f6ad55; --up:#3ecf8e; --down:#f56565; --blue:#5b8cff;
  --radius:12px; --maxw:1280px;
}
*{box-sizing:border-box}
html,body{margin:0;padding:0;background:var(--bg);color:var(--text);
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:var(--accent)}
button, select, input{font-family:inherit}
.wrap{max-width:var(--maxw);margin:0 auto;padding:0 20px}
header.topbar{position:sticky;top:0;z-index:50;background:rgba(11,15,20,.92);
  backdrop-filter:blur(6px);border-bottom:1px solid var(--border)}
.topbar-inner{display:flex;align-items:center;gap:20px;padding:14px 20px;max-width:var(--maxw);margin:0 auto}
.brand{font-weight:800;font-size:18px;letter-spacing:.2px}
.brand span{color:var(--accent)}
nav.tabs{display:flex;flex-wrap:wrap;gap:4px;margin-left:auto}
nav.tabs button{background:none;border:1px solid transparent;color:var(--muted);
  padding:8px 12px;border-radius:8px;cursor:pointer;font-size:13.5px;font-weight:600}
nav.tabs button:hover{color:var(--text);border-color:var(--border)}
nav.tabs button.active{background:var(--panel2);color:var(--text);border-color:var(--accent)}
main{max-width:var(--maxw);margin:0 auto;padding:24px 20px 80px}
.tabpanel{display:none}
.tabpanel.active{display:block}
.card{background:var(--panel);border:1px solid var(--border);border-radius:var(--radius);padding:20px;margin-bottom:18px}
.card h2{margin:0 0 4px;font-size:18px}
.card h3{margin:0 0 10px;font-size:14px;color:var(--muted);text-transform:uppercase;letter-spacing:.06em}
.grid{display:grid;gap:18px}
.grid.cols-2{grid-template-columns:1fr 1fr}
.grid.cols-3{grid-template-columns:1fr 1fr 1fr}
.grid.cols-4{grid-template-columns:repeat(4,1fr)}
@media(max-width:900px){.grid.cols-2,.grid.cols-3,.grid.cols-4{grid-template-columns:1fr}}
.hero{padding:40px 20px;text-align:left}
.hero h1{font-size:34px;margin:0 0 10px;line-height:1.15}
.hero p{color:var(--muted);font-size:16px;max-width:620px}
.cta-row{display:flex;gap:10px;flex-wrap:wrap;margin-top:18px}
.btn{background:var(--accent);color:#04211d;border:none;padding:10px 16px;border-radius:8px;
  font-weight:700;cursor:pointer;font-size:13.5px}
.btn.secondary{background:var(--panel2);color:var(--text);border:1px solid var(--border)}
.btn.ghost{background:none;color:var(--accent);border:1px solid var(--border)}
.btn.small{padding:6px 10px;font-size:12.5px}
.btn:disabled{opacity:.5;cursor:not-allowed}
.pill{display:inline-block;padding:3px 9px;border-radius:99px;font-size:11.5px;font-weight:700;
  background:var(--panel2);color:var(--muted);border:1px solid var(--border)}
.pill.up{color:var(--up);border-color:var(--up)}
.pill.down{color:var(--down);border-color:var(--down)}
table{width:100%;border-collapse:collapse;font-size:13.5px}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--border)}
th{color:var(--muted);font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.04em}
tr.clickable{cursor:pointer}
tr.clickable:hover{background:var(--panel2)}
.up{color:var(--up)}
.down{color:var(--down)}
.muted{color:var(--muted)}
input[type=text], input[type=number], input[type=email], input[type=date], select, textarea{
  background:var(--bg2);border:1px solid var(--border);color:var(--text);
  padding:8px 10px;border-radius:8px;font-size:13.5px;width:100%}
label{display:block;font-size:12.5px;color:var(--muted);margin-bottom:4px;margin-top:10px}
.row{display:flex;gap:10px;flex-wrap:wrap;align-items:center}
.chip{display:inline-flex;align-items:center;gap:6px;background:var(--panel2);border:1px solid var(--border);
  border-radius:99px;padding:5px 11px;font-size:12.5px;cursor:pointer;color:var(--text)}
.chip:hover{border-color:var(--accent)}
.chip.active{background:var(--accent);color:#04211d;border-color:var(--accent)}
.chip .x{opacity:.6;margin-left:2px}
.chart-wrap{position:relative;height:320px}
.chart-wrap.small{height:160px}
.badge-dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:6px}
.section-title{font-size:13px;color:var(--muted);text-transform:uppercase;letter-spacing:.08em;margin:22px 0 10px}
.footer-note{color:var(--muted);font-size:12.5px;margin-top:8px}
.status-table{max-width:640px}
.status-table td:first-child{color:var(--muted)}
.diag-ok{color:var(--up);font-weight:700}
.diag-bad{color:var(--down);font-weight:700}
.flex-between{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}
.small{font-size:12.5px}
.hidden{display:none !important}
::-webkit-scrollbar{height:8px;width:8px}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:8px}
.tag{font-size:11px;padding:2px 7px;border-radius:6px;background:var(--panel2);color:var(--muted);border:1px solid var(--border)}
.tag.private{color:var(--muted)}
.tag.filed{color:var(--blue);border-color:var(--blue)}
.tag.imminent{color:var(--accent2);border-color:var(--accent2)}
.tag.public{color:var(--up);border-color:var(--up)}
.kpi{padding:16px 18px}
.kpi .kpi-val{font-size:26px;font-weight:800;margin-top:2px;line-height:1.1}
.kpi .kpi-sub{font-size:11.5px;margin-top:3px}
.mkt-status{display:inline-flex;align-items:center;gap:7px;font-size:12px;font-weight:600;color:var(--muted);
  padding:5px 11px;border:1px solid var(--border);border-radius:99px;white-space:nowrap}
.mkt-status .dot{width:8px;height:8px;border-radius:50%;background:var(--muted)}
.mkt-status.open .dot{background:var(--up);box-shadow:0 0 0 3px rgba(62,207,142,.18)}
.mkt-status.closed .dot{background:var(--down)}
.topbar-inner .mkt-status{margin-left:8px}
footer.sitefoot{border-top:1px solid var(--border);margin-top:40px;padding:26px 20px;color:var(--muted);font-size:12.5px}
footer.sitefoot .wrap{max-width:var(--maxw);margin:0 auto;display:flex;justify-content:space-between;gap:20px;flex-wrap:wrap}
footer.sitefoot b{color:var(--text)}
@media(max-width:720px){ nav.tabs button{padding:7px 9px;font-size:12.5px} .hero h1{font-size:26px} .topbar-inner{gap:10px} }
"""


HTML_TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Growth Markets Research</title>
<meta name="description" content="Growth Markets Research: watchlists, technical + money-flow indicators, and rule-based alerts for growth sectors.">
<style>__CSS__</style>
</head>
<body>
<header class="topbar">
  <div class="topbar-inner">
    <div class="brand">Growth<span>Markets</span> Research</div>
    <span class="mkt-status" id="mkt-status"><span class="dot"></span><span id="mkt-status-text">Market</span></span>
    <nav class="tabs" id="tabnav"></nav>
  </div>
</header>
<main id="main"></main>
<footer class="sitefoot">
  <div class="wrap">
    <div><b>Growth Markets Research</b> &middot; watchlists, money-flow charting &amp; rule-based alerts. Runs $0/month on GitHub Pages + Actions.</div>
    <div>Data: Yahoo Finance / Stooq (best-effort). Not investment advice.</div>
  </div>
</footer>
<script>__CHARTJS__</script>
<script>
window.GMR_DATA = __SEED_DATA__;
window.GMR_DEPLOY_FILES = __DEPLOY_FILES__;
</script>
<script>__APP_JS__</script>
</body>
</html>
"""


def build():
    css = CSS
    chartjs = load_text("vendor/chart.umd.min.js")
    seed = build_seed_data()
    # APP_JS is assembled from the JS_* raw-string parts defined below this
    # function (gotcha #1: keep everything a single raw string / concat of
    # raw strings so a stray Python escape can't corrupt the JS output).
    app_js = APP_JS

    # Files the Methodology/Alerts tabs push into the user's repo via the
    # GitHub API when they turn on scheduled emails / arm alerts. Embedding
    # via json.dumps (not hand-written JS string literals) sidesteps gotcha
    # #1 entirely -- Python does the escaping, not a human.
    deploy_files = {
        "workflow": load_text(".github/workflows/nri-email.yml"),
        "sendScript": load_text("scripts/maybe_send_email.py"),
        "indicators": load_text("scripts/indicators.py"),
    }

    html = (
        HTML_TEMPLATE
        .replace("__CSS__", css)
        .replace("__CHARTJS__", chartjs)
        .replace("__SEED_DATA__", json.dumps(seed))
        .replace("__DEPLOY_FILES__", json.dumps(deploy_files))
        .replace("__APP_JS__", app_js)
    )

    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    # legacy filename kept for backward compatibility with old bookmarks/links
    with open(os.path.join(ROOT, "Nuclear-Renaissance-Index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    with open(os.path.join(ROOT, ".nojekyll"), "w", encoding="utf-8") as f:
        f.write("")

    size_kb = len(html.encode("utf-8")) / 1024
    print(f"Built index.html ({size_kb:.0f} KB) + Nuclear-Renaissance-Index.html + .nojekyll")


# ---------------------------------------------------------------------------
# APP_JS — assembled from raw-string parts. Keeping the JS as Python raw
# strings (gotcha #1) means backslashes are literal; never write \' inside a
# JS string literal here — use double quotes instead.
# ---------------------------------------------------------------------------

JS_OPEN = r"""
(function(){
"use strict";
"""

JS_CORE = r"""
// ---- tiny DOM + format helpers ----------------------------------------
function $(sel, root){ return (root||document).querySelector(sel); }
function $all(sel, root){ return Array.prototype.slice.call((root||document).querySelectorAll(sel)); }
function esc(s){
  return String(s == null ? "" : s).replace(/[&<>"]/g, function(c){
    return {"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;"}[c];
  });
}
function fmtPrice(v){ return (v == null || isNaN(v)) ? "--" : "$" + Number(v).toFixed(2); }
function fmtNum(v, d){ return (v == null || isNaN(v)) ? "--" : Number(v).toFixed(d == null ? 2 : d); }
function fmtPct(v, d){ return (v == null || isNaN(v)) ? "--" : (v >= 0 ? "+" : "") + Number(v).toFixed(d == null ? 2 : d) + "%"; }
function pctClass(v){ return (v == null || isNaN(v)) ? "" : (v >= 0 ? "up" : "down"); }
function todayISO(){ return new Date().toISOString().slice(0,10); }
function uid(){ return Math.random().toString(36).slice(2, 10); }

// ---- localStorage helpers (namespaced, never throw) --------------------
var LS_PREFIX = "gmr_";
function lsGet(key, fallback){
  try{
    var raw = localStorage.getItem(LS_PREFIX + key);
    return raw == null ? fallback : JSON.parse(raw);
  }catch(e){ return fallback; }
}
function lsSet(key, val){
  try{ localStorage.setItem(LS_PREFIX + key, JSON.stringify(val)); }catch(e){ /* quota or private mode */ }
}

// ---- global app state ---------------------------------------------------
var SEED = window.GMR_DATA || {};
var STATE = {
  tab: "dashboard",
  watchlists: lsGet("watchlists", SEED.watchlists),
  profile: lsGet("profile", SEED.profile),
  alerts: lsGet("alerts", SEED.alerts),
  emailSettings: lsGet("emailSettings", SEED.emailSettings),
  presets: SEED.presets || [],
  constituents: lsGet("constituents", SEED.constituents || []),
  catalysts: SEED.catalysts || [],
  preIpo: SEED.preIpo || [],
  seriesCache: {},
  githubToken: lsGet("githubToken", ""),
  githubRepo: lsGet("githubRepo", ""),
  deployFiles: window.GMR_DEPLOY_FILES || {}
};
function saveWatchlists(){ lsSet("watchlists", STATE.watchlists); }
function saveProfile(){ lsSet("profile", STATE.profile); }
function saveAlerts(){ lsSet("alerts", STATE.alerts); }
function saveEmailSettings(){ lsSet("emailSettings", STATE.emailSettings); }
function saveConstituents(){ lsSet("constituents", STATE.constituents); }

// ---- indicator math (mirrors scripts/indicators.py -- keep in sync) -----
var IND = {};
IND.sma = function(dates, closes, n){
  var out = [];
  for (var i=0;i<closes.length;i++){
    var p = null;
    if (i+1 >= n){
      var sum=0; for(var j=i-n+1;j<=i;j++) sum+=closes[j];
      p = sum/n;
    }
    out.push({d:dates[i], p:p});
  }
  return out;
};
IND.ema = function(dates, closes, n){
  var out = []; var k = 2/(n+1); var prev = null;
  for (var i=0;i<closes.length;i++){
    var p = null;
    if (prev == null){
      if (i+1 === n){
        var sum=0; for(var j=i-n+1;j<=i;j++) sum+=closes[j];
        prev = sum/n; p = prev;
      }
    } else {
      prev = closes[i]*k + prev*(1-k); p = prev;
    }
    out.push({d:dates[i], p:p});
  }
  return out;
};
IND.rsi = function(dates, closes, n){
  n = n || 14;
  var out = [];
  for (var i=0;i<closes.length;i++) out.push({d:dates[i], p:null});
  if (closes.length < n+1) return out;
  var gains=0, losses=0, i2;
  for (i2=1;i2<=n;i2++){
    var ch = closes[i2]-closes[i2-1];
    gains += Math.max(ch,0); losses += Math.max(-ch,0);
  }
  var avgGain = gains/n, avgLoss = losses/n;
  out[n].p = avgLoss===0 ? 100 : 100 - (100/(1+avgGain/avgLoss));
  for (i2=n+1;i2<closes.length;i2++){
    var change = closes[i2]-closes[i2-1];
    var gain = Math.max(change,0), loss = Math.max(-change,0);
    avgGain = (avgGain*(n-1)+gain)/n;
    avgLoss = (avgLoss*(n-1)+loss)/n;
    out[i2].p = avgLoss===0 ? 100 : 100 - (100/(1+avgGain/avgLoss));
  }
  return out;
};
IND.bollinger = function(dates, closes, n, k){
  n = n||20; k = k||2;
  var mid = IND.sma(dates, closes, n);
  var upper=[], lower=[];
  for (var i=0;i<closes.length;i++){
    if (mid[i].p != null){
      var m = mid[i].p, variance=0;
      for (var j=i-n+1;j<=i;j++) variance += Math.pow(closes[j]-m,2);
      variance/=n;
      var sd = Math.sqrt(variance);
      upper.push({d:dates[i], p:m+k*sd});
      lower.push({d:dates[i], p:m-k*sd});
    } else {
      upper.push({d:dates[i], p:null}); lower.push({d:dates[i], p:null});
    }
  }
  return {mid:mid, upper:upper, lower:lower};
};
IND.macd = function(dates, closes, fast, slow, signal){
  fast=fast||12; slow=slow||26; signal=signal||9;
  var emaFast = IND.ema(dates, closes, fast);
  var emaSlow = IND.ema(dates, closes, slow);
  var line = [];
  for (var i=0;i<closes.length;i++){
    var p = (emaFast[i].p!=null && emaSlow[i].p!=null) ? emaFast[i].p-emaSlow[i].p : null;
    line.push({d:dates[i], p:p});
  }
  var first = -1;
  for (i=0;i<line.length;i++){ if (line[i].p!=null){ first=i; break; } }
  var signalLine = line.map(function(x){ return {d:x.d, p:null}; });
  var hist = line.map(function(x){ return {d:x.d, p:null}; });
  if (first >= 0){
    var subDates = dates.slice(first), subCloses = line.slice(first).map(function(x){return x.p;});
    var subSignal = IND.ema(subDates, subCloses, signal);
    for (var j2=0;j2<subSignal.length;j2++){
      if (subSignal[j2].p!=null){
        signalLine[first+j2].p = subSignal[j2].p;
        hist[first+j2].p = line[first+j2].p - subSignal[j2].p;
      }
    }
  }
  return {line:line, signal:signalLine, hist:hist};
};
IND.vwap = function(dates, closes, volumes){
  var out=[]; var cumPV=0, cumV=0;
  for (var i=0;i<closes.length;i++){
    cumPV += closes[i]*(volumes[i]||0); cumV += (volumes[i]||0);
    out.push({d:dates[i], p: cumV ? cumPV/cumV : null});
  }
  return out;
};
IND.obv = function(dates, closes, volumes){
  var out=[{d:dates[0], p:0}];
  for (var i=1;i<closes.length;i++){
    var prev = out[i-1].p;
    if (closes[i] > closes[i-1]) out.push({d:dates[i], p: prev + (volumes[i]||0)});
    else if (closes[i] < closes[i-1]) out.push({d:dates[i], p: prev - (volumes[i]||0)});
    else out.push({d:dates[i], p: prev});
  }
  return out;
};
IND._atrProxy = function(closes, n){
  n = n||14;
  var changes = [null];
  for (var i=1;i<closes.length;i++) changes.push(Math.abs(closes[i]-closes[i-1]));
  var out = [];
  for (i=0;i<closes.length;i++){
    var lo = Math.max(0, i-n+1);
    var window = changes.slice(lo, i+1).filter(function(c){ return c!=null; });
    out.push(window.length>=n ? window.reduce(function(a,b){return a+b;},0)/window.length : null);
  }
  return out;
};
IND._mfm = function(close, prevClose, atr){
  if (!atr || atr<=0 || prevClose==null) return null;
  var m = 2*(close-prevClose)/atr;
  return Math.max(-1, Math.min(1, m));
};
IND.cmf = function(dates, closes, volumes, n){
  n = n||21;
  var atr = IND._atrProxy(closes, 14);
  var mfv = closes.map(function(){ return null; });
  for (var i=1;i<closes.length;i++){
    var m = IND._mfm(closes[i], closes[i-1], atr[i]);
    if (m!=null) mfv[i] = m*(volumes[i]||0);
  }
  var out=[];
  for (i=0;i<closes.length;i++){
    var lo = Math.max(0, i-n+1);
    var wv=[], wvol=[];
    for (var j=lo;j<=i;j++){ if (mfv[j]!=null){ wv.push(mfv[j]); wvol.push(volumes[j]||0); } }
    var volSum = wvol.reduce(function(a,b){return a+b;},0);
    out.push({d:dates[i], p: (wv.length>=n && volSum>0) ? wv.reduce(function(a,b){return a+b;},0)/volSum : null});
  }
  return out;
};
IND.mfi = function(dates, closes, volumes, n){
  n = n||14;
  var rawMf = closes.map(function(c,i){ return c*(volumes[i]||0); });
  var pos = closes.map(function(){return 0;}), neg = closes.map(function(){return 0;});
  for (var i=1;i<closes.length;i++){
    if (closes[i]>closes[i-1]) pos[i]=rawMf[i];
    else if (closes[i]<closes[i-1]) neg[i]=rawMf[i];
  }
  var out=[];
  for (i=0;i<closes.length;i++){
    var p = null;
    if (i+1 >= n+1){
      var posSum=0, negSum=0;
      for (var j=i-n+1;j<=i;j++){ posSum+=pos[j]; negSum+=neg[j]; }
      p = negSum===0 ? 100 : 100 - (100/(1+posSum/negSum));
    }
    out.push({d:dates[i], p:p});
  }
  return out;
};
IND.adLine = function(dates, closes, volumes){
  var atr = IND._atrProxy(closes, 14);
  var out=[{d:dates[0], p:0}]; var cum=0;
  for (var i=1;i<closes.length;i++){
    var m = IND._mfm(closes[i], closes[i-1], atr[i]);
    if (m!=null) cum += m*(volumes[i]||0);
    out.push({d:dates[i], p:cum});
  }
  return out;
};
IND.moneyFlowStatus = function(cmfSeries, lookback){
  lookback = lookback || 21;
  var vals = cmfSeries.slice(-lookback).map(function(x){return x.p;}).filter(function(v){return v!=null;});
  if (!vals.length) return {label:"Neutral", cmf:0, cls:""};
  var avg = vals.reduce(function(a,b){return a+b;},0)/vals.length;
  if (avg >= 0.05) return {label:"Accumulating", cmf:avg, cls:"up"};
  if (avg <= -0.05) return {label:"Distributing", cmf:avg, cls:"down"};
  return {label:"Neutral", cmf:avg, cls:""};
};
IND.obvNewHigh = function(obvSeries, n){
  var window = obvSeries.slice(-n).map(function(x){return x.p;}).filter(function(v){return v!=null;});
  if (window.length < 2) return false;
  return window[window.length-1] >= Math.max.apply(null, window);
};
// expose for console debugging / cross-checking against scripts/indicators.py
try{ window.GMR = window.GMR || {}; window.GMR.IND = IND; }catch(e){}
"""

JS_PROXY = r"""
// ---- CORS proxy chain ----------------------------------------------------
// Order matters: cheap/fast proxies first. Health state persists in
// localStorage so a bad proxy this session stays deprioritized next time.
// Verified against Yahoo from a GitHub Pages origin (2026-07). The free proxy
// landscape churns constantly -- corsproxy.io (403), thingproxy (dead), and
// r.jina.ai (401) all stopped working, so the chain leads with the ones that
// still return a valid Access-Control-Allow-Origin today and keeps a couple of
// backups. allorigins is the backbone but throws Cloudflare 5xx under load, so
// we retry the whole chain once before giving up.
var PROXIES = [
  {name:"allorigins-get", build:function(u){ return "https://api.allorigins.win/get?url=" + encodeURIComponent(u); }, wrapped:true},
  {name:"corssh",         build:function(u){ return "https://proxy.cors.sh/" + u; }},
  {name:"allorigins-raw", build:function(u){ return "https://api.allorigins.win/raw?url=" + encodeURIComponent(u); }},
  {name:"codetabs",       build:function(u){ return "https://api.codetabs.com/v1/proxy?quest=" + encodeURIComponent(u); }},
  {name:"corslol",        build:function(u){ return "https://api.cors.lol/?url=" + encodeURIComponent(u); }},
  {name:"thingproxy",     build:function(u){ return "https://thingproxy.freeboard.io/fetch/" + u; }}
];
function proxyHealth(){ return lsGet("proxyHealth", {}); }
function saveProxyHealth(h){ lsSet("proxyHealth", h); }
function orderedProxies(){
  var health = proxyHealth();
  var lastGood = lsGet("lastGoodProxy", null);
  var list = PROXIES.slice();
  list.sort(function(a,b){
    if (a.name === lastGood) return -1;
    if (b.name === lastGood) return 1;
    var fa = (health[a.name]||{}).fails||0, fb = (health[b.name]||{}).fails||0;
    return fa - fb;
  });
  return list.filter(function(p){ return (health[p.name]||{}).fails < 5; });
}
function markProxyResult(name, ok){
  var health = proxyHealth();
  health[name] = health[name] || {fails:0};
  if (ok){ health[name].fails = 0; lsSet("lastGoodProxy", name); }
  else { health[name].fails = (health[name].fails||0) + 1; }
  saveProxyHealth(health);
}
function fetchViaProxies(targetUrl, timeoutMs){
  timeoutMs = timeoutMs || 7000;
  var list = orderedProxies();
  function tryOne(idx){
    if (idx >= list.length) return Promise.reject(new Error("all proxies exhausted"));
    var proxy = list[idx];
    var ctrl = (typeof AbortController !== "undefined") ? new AbortController() : null;
    var timer = ctrl ? setTimeout(function(){ ctrl.abort(); }, timeoutMs) : null;
    return fetch(proxy.build(targetUrl), ctrl ? {signal: ctrl.signal} : {})
      .then(function(res){
        if (timer) clearTimeout(timer);
        if (!res.ok) throw new Error("http " + res.status);
        return res.text().then(function(txt){
          if (!txt || !txt.length) throw new Error("empty body");
          if (proxy.wrapped){
            try{ txt = JSON.parse(txt).contents || ""; }catch(e){ throw new Error("bad wrapped body"); }
            if (!txt) throw new Error("empty wrapped body");
          }
          markProxyResult(proxy.name, true);
          return txt;
        });
      })
      .catch(function(err){
        markProxyResult(proxy.name, false);
        return tryOne(idx+1);
      });
  }
  return tryOne(0);
}

// ---- price series fetch: Yahoo first, Stooq fallback ---------------------
function parseYahooChart(json){
  var res = JSON.parse(json).chart.result[0];
  var ts = res.timestamp || [];
  var closes = res.indicators.quote[0].close || [];
  var volumes = res.indicators.quote[0].volume || [];
  var dates = ts.map(function(t){ return new Date(t*1000).toISOString().slice(0,10); });
  var out = {dates:[], closes:[], volumes:[]};
  for (var i=0;i<dates.length;i++){
    if (closes[i]!=null){ out.dates.push(dates[i]); out.closes.push(closes[i]); out.volumes.push(volumes[i]||0); }
  }
  return out;
}
function parseStooqCsv(csv){
  var lines = csv.trim().split("\n").slice(1);
  var out = {dates:[], closes:[], volumes:[]};
  lines.forEach(function(line){
    var parts = line.split(",");
    if (parts.length < 6) return;
    var close = parseFloat(parts[4]), vol = parseFloat(parts[5]);
    if (isNaN(close)) return;
    out.dates.push(parts[0]); out.closes.push(close); out.volumes.push(isNaN(vol)?0:vol);
  });
  return out;
}
function syntheticSeries(ticker, days){
  // Deterministic seeded random walk with mild drift + occasional volatility
  // clusters, so the offline fallback looks like a believable price chart
  // (not an obvious sine wave) and money-flow/RSI read naturally.
  days = days || 260;
  var seed = 0; for (var i=0;i<ticker.length;i++) seed += (i+1)*ticker.charCodeAt(i);
  // mulberry32 PRNG
  var a = (seed ^ 0x9e3779b9) >>> 0;
  function rnd(){
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    var t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  }
  var price = 20 + (seed % 180);
  var drift = (rnd() - 0.45) * 0.0012;       // small per-ticker trend
  var vol = 0.012 + rnd() * 0.02;            // base daily volatility
  var dates=[], closes=[], volumes=[];
  var d = new Date(); d.setDate(d.getDate()-days);
  for (i=0;i<days;i++){
    var day = d.getDay();
    if (day!==0 && day!==6){
      // gaussian-ish shock via sum of uniforms; occasional vol spike
      var shock = (rnd()+rnd()+rnd()-1.5) * vol;
      if (rnd() > 0.97) shock *= 3;
      price = Math.max(1, price*(1 + drift + shock));
      dates.push(new Date(d).toISOString().slice(0,10));
      closes.push(Math.round(price*100)/100);
      var baseVol = 400000 + (seed % 9)*300000;
      volumes.push(Math.round(baseVol * (0.6 + rnd()*1.6)));
    }
    d.setDate(d.getDate()+1);
  }
  return {dates:dates, closes:closes, volumes:volumes, synthetic:true};
}
function getSeries(ticker, range){
  ticker = ticker.toUpperCase();
  range = range || "2y";
  var cacheKey = ticker + "::" + range;
  if (STATE.seriesCache[cacheKey]) return Promise.resolve(STATE.seriesCache[cacheKey]);
  var yahooUrl = "https://query1.finance.yahoo.com/v8/finance/chart/" + encodeURIComponent(ticker) + "?range=" + range + "&interval=1d";
  var stooqUrl = "https://stooq.com/q/d/l/?s=" + encodeURIComponent(ticker.toLowerCase()) + ".us&i=d";

  // 1) Baked same-origin data, refreshed by the refresh-quotes workflow. This
  //    is served from our own GitHub Pages origin, so there is NO CORS and no
  //    proxy dependency -- it is the reliable path and covers every constituent
  //    + preset ticker. (Files live at data/quotes/{TICKER}.json.)
  function baked(){
    return fetch("data/quotes/" + encodeURIComponent(ticker) + ".json", {cache:"default"})
      .then(function(r){ if (!r.ok) throw new Error("no baked " + r.status); return r.json(); })
      .then(function(j){
        if (!j.closes || j.closes.length < 5) throw new Error("baked too short");
        return {dates:j.dates, closes:j.closes, volumes:j.volumes, updated:j.updated};
      });
  }

  // 2) Live proxy chain against Yahoo, then Stooq -- used for arbitrary tickers
  //    (Companies search) not in the baked set, or when baked data is missing.
  function attempt(){
    return fetchViaProxies(yahooUrl)
      .then(function(txt){ return parseYahooChart(txt); })
      .catch(function(){
        return fetchViaProxies(stooqUrl).then(function(txt){ return parseStooqCsv(txt); });
      })
      .then(function(series){
        if (!series.closes || series.closes.length < 5) throw new Error("no data");
        return series;
      });
  }

  return baked()
    .catch(function(){
      // not baked -- try the live proxy chain, retrying once (allorigins 5xx).
      return attempt().catch(function(){
        return new Promise(function(res){ setTimeout(res, 700); }).then(attempt);
      });
    })
    .then(function(series){
      STATE.seriesCache[cacheKey] = series;
      return series;
    })
    .catch(function(err){
      console.warn("GMR: no baked or live data for " + ticker + ", using synthetic series.", err);
      var rangeDays = {"1y":260,"2y":520,"5y":1300,"10y":2600,"max":2600}[range] || 260;
      var s = syntheticSeries(ticker, rangeDays);
      STATE.seriesCache[cacheKey] = s;
      return s;
    });
}
"""

JS_ROUTER = r"""
// ---- tabs / router ---------------------------------------------------
var TABS = [
  {key:"dashboard",   label:"Dashboard"},
  {key:"watchlists",  label:"Watchlists"},
  {key:"companies",   label:"Companies"},
  {key:"optimizer",   label:"Optimizer"},
  {key:"backtest",    label:"Backtest"},
  {key:"updates",     label:"Updates"},
  {key:"preipo",      label:"Pre-IPO"},
  {key:"profile",     label:"Profile"},
  {key:"alerts",      label:"Alerts"},
  {key:"methodology", label:"Methodology"}
];
var RENDERERS = {};
function renderNav(){
  var nav = $("#tabnav");
  nav.innerHTML = "";
  TABS.forEach(function(t){
    var b = document.createElement("button");
    b.textContent = t.label;
    b.dataset.tab = t.key;
    if (t.key === STATE.tab) b.className = "active";
    b.addEventListener("click", function(){ showTab(t.key); });
    nav.appendChild(b);
  });
}
function showTab(key){
  STATE.tab = key;
  location.hash = key;
  $all("#tabnav button").forEach(function(b){ b.className = (b.dataset.tab===key) ? "active" : ""; });
  var main = $("#main");
  main.innerHTML = "";
  var panel = document.createElement("div");
  panel.className = "tabpanel active";
  main.appendChild(panel);
  try{
    var renderer = RENDERERS[key];
    if (renderer) renderer(panel);
    else panel.innerHTML = "<div class=card><h2>" + esc(key) + "</h2><p class=muted>Coming online shortly.</p></div>";
  }catch(e){
    console.error("GMR: render failed for tab " + key, e);
    panel.innerHTML = "<div class=card><h2>This tab hit a snag</h2><p class=muted>Check the browser console for details. Other tabs are unaffected.</p></div>";
  }
}
function updateMarketStatus(){
  var el = document.getElementById("mkt-status");
  var txt = document.getElementById("mkt-status-text");
  if (!el || !txt) return;
  // US regular session 9:30-16:00 ET. Convert now to ET via the UTC offset
  // for America/New_York (handles DST via Intl, falling back to -4).
  var now = new Date();
  var etString = now.toLocaleString("en-US", {timeZone:"America/New_York", hour12:false, weekday:"short", hour:"2-digit", minute:"2-digit"});
  var parts = etString.match(/(\w{3}).*?(\d{2}):(\d{2})/);
  var open = false;
  if (parts){
    var day = parts[1], hh = parseInt(parts[2],10), mm = parseInt(parts[3],10);
    var isWeekday = ["Mon","Tue","Wed","Thu","Fri"].indexOf(day) !== -1;
    var mins = hh*60 + mm;
    open = isWeekday && mins >= (9*60+30) && mins < (16*60);
  }
  el.className = "mkt-status " + (open ? "open" : "closed");
  txt.textContent = open ? "Market open" : "Market closed";
}

function init(){
  renderNav();
  updateMarketStatus();
  setInterval(updateMarketStatus, 60000);
  var initial = (location.hash||"").replace("#","");
  var valid = TABS.some(function(t){ return t.key===initial; });
  showTab(valid ? initial : "dashboard");
  window.addEventListener("hashchange", function(){
    var k = location.hash.replace("#","");
    if (TABS.some(function(t){ return t.key===k; })) showTab(k);
  });
}
"""

JS_CLOSE = r"""
try{ init(); }
catch(e){
  console.error("GMR: fatal init error", e);
  document.getElementById("main").innerHTML =
    "<div class='card'><h2>Something went wrong loading Growth Markets Research</h2>" +
    "<p class='muted'>Open the browser console for details, then reload.</p></div>";
}
})();
"""

JS_DASHBOARD = r"""
// ---- Dashboard tab -------------------------------------------------------
RENDERERS.dashboard = function(root){
  root.innerHTML =
    "<div class='hero card'>" +
      "<h1>Spot growth before it moves.</h1>" +
      "<p>Track named watchlists across 30+ sectors, layer on technical and money-flow indicators, and fire rule-based alerts during market hours -- all for free.</p>" +
      "<div class='cta-row'>" +
        "<button class='btn' id='cta-watchlists'>Open Watchlists</button>" +
        "<button class='btn secondary' id='cta-alerts'>Set up an alert</button>" +
        "<button class='btn ghost' id='cta-optimizer'>Build a portfolio</button>" +
      "</div>" +
    "</div>" +
    "<div class='grid cols-4' id='dash-kpis'>" +
      "<div class='card kpi'><h3>Index Level</h3><div class='kpi-val' id='kpi-level'>--</div><div class='kpi-sub muted'>rebased to 100</div></div>" +
      "<div class='card kpi'><h3>Index Day Change</h3><div class='kpi-val' id='kpi-change'>--</div><div class='kpi-sub muted' id='kpi-change-sub'>vs prior close</div></div>" +
      "<div class='card kpi'><h3>Money-Flow Breadth</h3><div class='kpi-val' id='kpi-breadth'>--</div><div class='kpi-sub muted'>accumulating / total</div></div>" +
      "<div class='card kpi'><h3>Top Mover Today</h3><div class='kpi-val' id='kpi-topmover'>--</div><div class='kpi-sub muted' id='kpi-topmover-sub'>&nbsp;</div></div>" +
    "</div>" +
    "<div class='grid cols-2'>" +
      "<div class='card'><h3>Featured Index -- Nuclear</h3><div class='chart-wrap'><canvas id='dash-index-chart'></canvas></div></div>" +
      "<div class='card'><h3>Sector Weights</h3><div class='chart-wrap'><canvas id='dash-sector-donut'></canvas></div></div>" +
    "</div>" +
    "<div class='card'>" +
      "<h3>Your Watchlists</h3>" +
      "<div id='dash-watchlist-summary'></div>" +
    "</div>";

  $("#cta-watchlists").addEventListener("click", function(){ showTab("watchlists"); });
  $("#cta-alerts").addEventListener("click", function(){ showTab("alerts"); });
  $("#cta-optimizer").addEventListener("click", function(){ showTab("optimizer"); });

  renderWatchlistSummary($("#dash-watchlist-summary"));
  renderSectorDonut($("#dash-sector-donut"));
  renderIndexChart($("#dash-index-chart"));
  renderDashboardKPIs();
};

function renderDashboardKPIs(){
  var cons = STATE.constituents || [];
  if (!cons.length) return;
  Promise.all(cons.map(function(c){ return getSeries(c.ticker).then(function(s){ return {con:c, series:s}; }); })).then(function(rows){
    var totalWeight = cons.reduce(function(a,c){ return a+c.weight; }, 0);
    var lenRef = rows[0].series.closes.length;
    // weighted composite level + day change
    var levelNow = 0, levelPrev = 0;
    rows.forEach(function(r){
      var closes = r.series.closes, base = closes[0];
      if (!base) return;
      var now = closes[closes.length-1], prev = closes.length>1 ? closes[closes.length-2] : now;
      levelNow += (now/base)*100 * r.con.weight;
      levelPrev += (prev/base)*100 * r.con.weight;
    });
    levelNow /= totalWeight; levelPrev /= totalWeight;
    var dayChg = levelPrev ? (levelNow/levelPrev - 1)*100 : 0;

    // breadth: how many constituents are accumulating on money flow
    var accum = 0;
    var movers = [];
    rows.forEach(function(r){
      var s = r.series;
      var cmf = IND.cmf(s.dates, s.closes, s.volumes, 21);
      var status = IND.moneyFlowStatus(cmf, 21);
      if (status.cls === "up") accum++;
      var closes = s.closes;
      var chg = closes.length>1 ? (closes[closes.length-1]/closes[closes.length-2]-1)*100 : 0;
      movers.push({ticker:r.con.ticker, chg:chg});
    });
    movers.sort(function(a,b){ return Math.abs(b.chg)-Math.abs(a.chg); });
    var top = movers[0];

    var elLevel = $("#kpi-level"); if (elLevel) elLevel.textContent = fmtNum(levelNow, 1);
    var elChg = $("#kpi-change");
    if (elChg){ elChg.textContent = fmtPct(dayChg); elChg.className = "kpi-val " + pctClass(dayChg); }
    var elBreadth = $("#kpi-breadth"); if (elBreadth) elBreadth.textContent = accum + " / " + rows.length;
    var elTop = $("#kpi-topmover");
    if (elTop && top){ elTop.textContent = top.ticker; elTop.className = "kpi-val " + pctClass(top.chg); }
    var elTopSub = $("#kpi-topmover-sub"); if (elTopSub && top) elTopSub.textContent = fmtPct(top.chg) + " today";
  }).catch(function(e){ console.error("GMR: dashboard KPIs failed", e); });
}

function renderWatchlistSummary(root){
  var lists = STATE.watchlists.lists || {};
  var keys = Object.keys(lists);
  if (!keys.length){ root.innerHTML = "<p class='muted'>No watchlists yet.</p>"; return; }
  var html = "<table><thead><tr><th>List</th><th>Tickers</th><th></th></tr></thead><tbody>";
  keys.forEach(function(k){
    var l = lists[k];
    html += "<tr><td>" + esc(l.label||k) + "</td><td class='muted'>" + (l.tickers||[]).length + " names</td>" +
      "<td><button class='btn small ghost' data-open-list='" + esc(k) + "'>Open</button></td></tr>";
  });
  html += "</tbody></table>";
  root.innerHTML = html;
  $all("[data-open-list]", root).forEach(function(b){
    b.addEventListener("click", function(){
      lsSet("activeWatchlist", b.dataset.openList);
      showTab("watchlists");
    });
  });
}

function renderSectorDonut(canvas){
  var cons = STATE.constituents || [];
  var bySector = {};
  cons.forEach(function(c){ bySector[c.sector] = (bySector[c.sector]||0) + c.weight; });
  var labels = Object.keys(bySector);
  var colors = ["#4fd1c5","#f6ad55","#5b8cff","#3ecf8e","#f56565","#a78bfa","#f472b6","#facc15","#22d3ee","#fb923c"];
  new Chart(canvas.getContext("2d"), {
    type: "doughnut",
    data: {
      labels: labels,
      datasets: [{ data: labels.map(function(l){ return bySector[l]; }), backgroundColor: labels.map(function(l,i){ return colors[i % colors.length]; }) }]
    },
    options: { plugins: { legend: { position: "right", labels: { color: "#93a2bb", boxWidth: 12 } } }, maintainAspectRatio:false }
  });
}

function renderIndexChart(canvas){
  var cons = STATE.constituents || [];
  var tickers = cons.map(function(c){ return c.ticker; });
  Promise.all(tickers.map(function(t){ return getSeries(t); })).then(function(seriesList){
    var totalWeight = cons.reduce(function(a,c){ return a+c.weight; }, 0);
    var baseDates = seriesList[0] ? seriesList[0].dates : [];
    var composite = baseDates.map(function(d, i){
      var sum = 0, wsum = 0;
      seriesList.forEach(function(s, idx){
        if (!s.closes[0]) return;
        var norm = s.closes[i] != null ? (s.closes[i]/s.closes[0])*100 : (s.closes[s.closes.length-1]/s.closes[0])*100;
        sum += norm * cons[idx].weight; wsum += cons[idx].weight;
      });
      return wsum ? sum/wsum : null;
    });
    new Chart(canvas.getContext("2d"), {
      type: "line",
      data: { labels: baseDates, datasets: [{ label:"GMR Nuclear Index", data: composite, borderColor:"#4fd1c5", backgroundColor:"rgba(79,209,197,.12)", fill:true, pointRadius:0, tension:.15 }] },
      options: { maintainAspectRatio:false, scales:{ x:{ ticks:{ color:"#93a2bb", maxTicksLimit:8 }, grid:{color:"#1b2536"} }, y:{ ticks:{color:"#93a2bb"}, grid:{color:"#1b2536"} } }, plugins:{ legend:{ labels:{ color:"#93a2bb" } } } }
    });
  }).catch(function(e){ console.error("GMR: index chart failed", e); canvas.parentElement.innerHTML = "<p class='muted'>Chart unavailable right now.</p>"; });
}
"""

JS_WATCHLISTS = r"""
// ---- Watchlists tab -------------------------------------------------------
var WL_EXPANDED = null;
var DEFAULT_INDICATORS = {sma:true, ema:false, rsi:true, bollinger:false, macd:true, vwap:false};

function activeListKey(){
  var override = lsGet("activeWatchlist", null);
  if (override && STATE.watchlists.lists[override]) { lsSet("activeWatchlist", null); return override; }
  var keys = Object.keys(STATE.watchlists.lists);
  if (STATE.watchlists.active && STATE.watchlists.lists[STATE.watchlists.active]) return STATE.watchlists.active;
  return keys[0];
}

RENDERERS.watchlists = function(root){
  var activeKey = activeListKey();
  STATE.watchlists.active = activeKey;

  root.innerHTML =
    "<div class='card'>" +
      "<div class='flex-between'>" +
        "<div><h2>Watchlists</h2><p class='muted small'>Your named baskets. Clone a preset below or build your own.</p></div>" +
        "<div class='row'><input id='wl-new-name' type='text' placeholder='New list name' style='width:180px'><button class='btn small' id='wl-new-btn'>New list</button></div>" +
      "</div>" +
      "<div class='row' id='wl-list-chips' style='margin-top:14px'></div>" +
    "</div>" +
    "<div class='card'>" +
      "<h3>30+ Sector Presets</h3>" +
      "<div class='row' id='wl-preset-chips'></div>" +
    "</div>" +
    "<div id='wl-active-panel'></div>" +
    "<div class='card'>" +
      "<h3>Source Transparency</h3>" +
      "<p class='muted small'>These preset lists are hand-curated starting points -- large/mid-cap US-listed names with pure-play or near-pure-play exposure to each theme. They are not investment advice, not optimized, and not exhaustive. Prices are best-effort from Yahoo Finance / Stooq via public CORS proxies and can lag or fall back to a synthetic series if every proxy is unavailable.</p>" +
    "</div>";

  $("#wl-new-btn").addEventListener("click", function(){
    var name = ($("#wl-new-name").value||"").trim();
    if (!name) return;
    var key = name.toLowerCase().replace(/[^a-z0-9]+/g,"-").replace(/(^-|-$)/g,"") || uid();
    STATE.watchlists.lists[key] = {label:name, desc:"", tickers:[], indicators: Object.assign({}, DEFAULT_INDICATORS)};
    STATE.watchlists.active = key;
    saveWatchlists();
    showTab("watchlists");
  });

  renderListChips();
  renderPresetChips();
  renderActiveListPanel();
};

function renderListChips(){
  var root = $("#wl-list-chips");
  var lists = STATE.watchlists.lists;
  var keys = Object.keys(lists);
  if (!keys.length){ root.innerHTML = "<span class='muted small'>No lists yet -- clone a preset below to get started.</span>"; return; }
  root.innerHTML = keys.map(function(k){
    var active = k === STATE.watchlists.active;
    return "<span class='chip" + (active?" active":"") + "' data-list-key='" + esc(k) + "'>" + esc(lists[k].label||k) + "</span>";
  }).join("");
  $all("[data-list-key]", root).forEach(function(chip){
    chip.addEventListener("click", function(){
      STATE.watchlists.active = chip.dataset.listKey;
      saveWatchlists();
      WL_EXPANDED = null;
      showTab("watchlists");
    });
  });
}

function renderPresetChips(){
  var root = $("#wl-preset-chips");
  root.innerHTML = STATE.presets.map(function(p){
    return "<span class='chip' data-preset-key='" + esc(p.key) + "' title='" + esc(p.desc) + "'>" + esc(p.label) + "</span>";
  }).join("");
  $all("[data-preset-key]", root).forEach(function(chip){
    chip.addEventListener("click", function(){
      var preset = STATE.presets.filter(function(p){ return p.key === chip.dataset.presetKey; })[0];
      if (!preset) return;
      STATE.watchlists.lists[preset.key] = {
        label: preset.label, desc: preset.desc, tickers: preset.tickers.slice(),
        indicators: Object.assign({}, DEFAULT_INDICATORS)
      };
      STATE.watchlists.active = preset.key;
      saveWatchlists();
      WL_EXPANDED = null;
      showTab("watchlists");
    });
  });
}

function renderActiveListPanel(){
  var root = $("#wl-active-panel");
  var key = STATE.watchlists.active;
  var list = STATE.watchlists.lists[key];
  if (!list){ root.innerHTML = ""; return; }
  list.indicators = list.indicators || Object.assign({}, DEFAULT_INDICATORS);

  root.innerHTML =
    "<div class='card'>" +
      "<div class='flex-between'>" +
        "<div><h2>" + esc(list.label||key) + "</h2>" + (list.desc ? "<p class='muted small'>" + esc(list.desc) + "</p>" : "") + "</div>" +
        "<div class='row'><input id='wl-add-ticker' type='text' placeholder='Add ticker' style='width:120px;text-transform:uppercase'><button class='btn small' id='wl-add-btn'>Add</button></div>" +
      "</div>" +
      "<div class='row' style='margin-top:10px' id='wl-indicator-toggles'></div>" +
      "<div style='margin-top:14px' id='wl-table-wrap'><p class='muted small'>Loading quotes...</p></div>" +
      "<div id='wl-chart-wrap'></div>" +
    "</div>";

  ["sma","ema","rsi","bollinger","macd","vwap"].forEach(function(ind){
    var wrap = document.createElement("label");
    wrap.className = "chip" + (list.indicators[ind] ? " active" : "");
    wrap.style.cursor = "pointer";
    wrap.textContent = ind.toUpperCase();
    wrap.addEventListener("click", function(){
      list.indicators[ind] = !list.indicators[ind];
      saveWatchlists();
      renderActiveListPanel();
    });
    $("#wl-indicator-toggles").appendChild(wrap);
  });

  $("#wl-add-btn").addEventListener("click", function(){
    var t = ($("#wl-add-ticker").value||"").trim().toUpperCase();
    if (!t) return;
    if (list.tickers.indexOf(t) === -1) list.tickers.push(t);
    saveWatchlists();
    renderActiveListPanel();
  });

  renderWatchlistTable(list);
}

function renderWatchlistTable(list){
  var wrap = $("#wl-table-wrap");
  if (!list.tickers.length){ wrap.innerHTML = "<p class='muted small'>No tickers yet -- add one above.</p>"; return; }

  Promise.all(list.tickers.map(function(t){ return getSeries(t).then(function(s){ return {ticker:t, series:s}; }); }))
    .then(function(results){
      var rows = results.map(function(r){
        var s = r.series;
        var closes = s.closes, dates = s.dates, volumes = s.volumes;
        var price = closes[closes.length-1];
        var chg = closes.length>1 ? ((price/closes[closes.length-2])-1)*100 : null;
        var rsiSeries = IND.rsi(dates, closes, 14);
        var mfiSeries = IND.mfi(dates, closes, volumes, 14);
        var cmfSeries = IND.cmf(dates, closes, volumes, 21);
        var status = IND.moneyFlowStatus(cmfSeries, 21);
        var rsiVal = rsiSeries[rsiSeries.length-1].p;
        var mfiVal = mfiSeries[mfiSeries.length-1].p;
        return {ticker:r.ticker, price:price, chg:chg, rsi:rsiVal, mfi:mfiVal, status:status, synthetic:s.synthetic};
      });
      var html = "<table><thead><tr><th>Ticker</th><th>Price</th><th>Chg</th><th>RSI(14)</th><th>MFI(14)</th><th>Money Flow</th><th></th></tr></thead><tbody>";
      rows.forEach(function(row){
        html += "<tr class='clickable' data-row-ticker='" + esc(row.ticker) + "'>" +
          "<td>" + esc(row.ticker) + (row.synthetic ? " <span class='tag'>sample data</span>" : "") + "</td>" +
          "<td>" + fmtPrice(row.price) + "</td>" +
          "<td class='" + pctClass(row.chg) + "'>" + fmtPct(row.chg) + "</td>" +
          "<td>" + fmtNum(row.rsi, 1) + "</td>" +
          "<td>" + fmtNum(row.mfi, 1) + "</td>" +
          "<td><span class='pill " + row.status.cls + "'>" + row.status.label + "</span></td>" +
          "<td><button class='btn small ghost' data-remove-ticker='" + esc(row.ticker) + "'>Remove</button></td>" +
        "</tr>";
      });
      html += "</tbody></table>";
      wrap.innerHTML = html;

      $all("[data-remove-ticker]", wrap).forEach(function(b){
        b.addEventListener("click", function(e){
          e.stopPropagation();
          list.tickers = list.tickers.filter(function(t){ return t !== b.dataset.removeTicker; });
          saveWatchlists();
          renderActiveListPanel();
        });
      });
      $all("[data-row-ticker]", wrap).forEach(function(tr){
        tr.addEventListener("click", function(){
          WL_EXPANDED = (WL_EXPANDED === tr.dataset.rowTicker) ? null : tr.dataset.rowTicker;
          renderWatchlistChart(list);
        });
      });

      renderWatchlistChart(list);
    })
    .catch(function(e){
      console.error("GMR: watchlist table failed", e);
      wrap.innerHTML = "<p class='muted small'>Could not load quotes right now.</p>";
    });
}

function renderWatchlistChart(list){
  var wrap = $("#wl-chart-wrap");
  if (!WL_EXPANDED || list.tickers.indexOf(WL_EXPANDED) === -1){ wrap.innerHTML = ""; return; }
  var ticker = WL_EXPANDED;
  wrap.innerHTML =
    "<div class='section-title'>" + esc(ticker) + " chart</div>" +
    "<div class='chart-wrap'><canvas id='wl-price-canvas'></canvas></div>" +
    "<div class='chart-wrap small' id='wl-osc-wrap'><canvas id='wl-osc-canvas'></canvas></div>";

  getSeries(ticker).then(function(s){
    var ind = list.indicators;
    var datasets = [{ label:ticker, data:s.closes, borderColor:"#e7edf7", borderWidth:1.6, pointRadius:0, tension:.1 }];
    if (ind.sma) datasets.push({ label:"SMA20", data: IND.sma(s.dates, s.closes, 20).map(function(x){return x.p;}), borderColor:"#4fd1c5", pointRadius:0, borderWidth:1.2, tension:.1 });
    if (ind.ema) datasets.push({ label:"EMA20", data: IND.ema(s.dates, s.closes, 20).map(function(x){return x.p;}), borderColor:"#f6ad55", pointRadius:0, borderWidth:1.2, tension:.1 });
    if (ind.vwap) datasets.push({ label:"VWAP", data: IND.vwap(s.dates, s.closes, s.volumes).map(function(x){return x.p;}), borderColor:"#5b8cff", pointRadius:0, borderWidth:1.2, tension:.1 });
    if (ind.bollinger){
      var b = IND.bollinger(s.dates, s.closes, 20, 2);
      datasets.push({ label:"BB Upper", data:b.upper.map(function(x){return x.p;}), borderColor:"#93a2bb", borderDash:[4,3], pointRadius:0, borderWidth:1 });
      datasets.push({ label:"BB Lower", data:b.lower.map(function(x){return x.p;}), borderColor:"#93a2bb", borderDash:[4,3], pointRadius:0, borderWidth:1 });
    }
    new Chart($("#wl-price-canvas").getContext("2d"), {
      type:"line", data:{ labels:s.dates, datasets:datasets },
      options:{ maintainAspectRatio:false, scales:{ x:{ ticks:{color:"#93a2bb", maxTicksLimit:8}, grid:{color:"#1b2536"} }, y:{ ticks:{color:"#93a2bb"}, grid:{color:"#1b2536"} } }, plugins:{ legend:{ labels:{color:"#93a2bb", boxWidth:12} } } }
    });

    var oscWrap = $("#wl-osc-wrap");
    if (ind.macd){
      var m = IND.macd(s.dates, s.closes);
      new Chart($("#wl-osc-canvas").getContext("2d"), {
        type:"line",
        data:{ labels:s.dates, datasets:[
          { label:"MACD", data:m.line.map(function(x){return x.p;}), borderColor:"#4fd1c5", pointRadius:0, borderWidth:1.2 },
          { label:"Signal", data:m.signal.map(function(x){return x.p;}), borderColor:"#f6ad55", pointRadius:0, borderWidth:1.2 }
        ]},
        options:{ maintainAspectRatio:false, scales:{ x:{ ticks:{color:"#93a2bb", maxTicksLimit:8}, grid:{color:"#1b2536"} }, y:{ ticks:{color:"#93a2bb"}, grid:{color:"#1b2536"} } }, plugins:{ legend:{ labels:{color:"#93a2bb", boxWidth:12} } } }
      });
    } else if (ind.rsi){
      var r = IND.rsi(s.dates, s.closes, 14);
      new Chart($("#wl-osc-canvas").getContext("2d"), {
        type:"line",
        data:{ labels:s.dates, datasets:[{ label:"RSI(14)", data:r.map(function(x){return x.p;}), borderColor:"#a78bfa", pointRadius:0, borderWidth:1.2 }] },
        options:{ maintainAspectRatio:false, scales:{ x:{ ticks:{color:"#93a2bb", maxTicksLimit:8}, grid:{color:"#1b2536"} }, y:{ min:0, max:100, ticks:{color:"#93a2bb"}, grid:{color:"#1b2536"} } }, plugins:{ legend:{ labels:{color:"#93a2bb", boxWidth:12} } } }
      });
    } else {
      oscWrap.innerHTML = "<p class='muted small'>Toggle RSI or MACD above to see an oscillator pane.</p>";
    }
  });
}
"""

JS_COMPANIES = r"""
// ---- Companies tab ---------------------------------------------------
var CO_TICKER = lsGet("companiesTicker", "CCJ");
var CO_COMPARE = lsGet("companiesCompare", ["CCJ", "CEG", "LEU"]);

function tickerName(ticker){
  var hit = STATE.constituents.filter(function(c){ return c.ticker === ticker; })[0];
  return hit ? hit.name : ticker;
}

RENDERERS.companies = function(root){
  root.innerHTML =
    "<div class='hero card'>" +
      "<h1>Look up any US-listed ticker.</h1>" +
      "<p>Live chart, key metrics, and money-flow signals -- then compare it against other names.</p>" +
      "<div class='cta-row'>" +
        "<input id='co-search' type='text' placeholder='e.g. NVDA' style='width:200px;text-transform:uppercase'>" +
        "<button class='btn' id='co-search-btn'>Search</button>" +
      "</div>" +
    "</div>" +
    "<div id='co-detail'></div>" +
    "<div class='card'>" +
      "<h3>Compare Multiple Stocks</h3>" +
      "<div class='row' id='co-compare-chips'></div>" +
      "<div class='row' style='margin-top:10px'><input id='co-compare-add' type='text' placeholder='Add ticker to compare' style='width:180px;text-transform:uppercase'><button class='btn small' id='co-compare-add-btn'>Add</button></div>" +
      "<div class='chart-wrap' style='margin-top:14px'><canvas id='co-compare-canvas'></canvas></div>" +
      "<div id='co-compare-table' style='margin-top:12px'></div>" +
    "</div>";

  $("#co-search").value = CO_TICKER;
  function doSearch(){
    var t = ($("#co-search").value||"").trim().toUpperCase();
    if (!t) return;
    CO_TICKER = t; lsSet("companiesTicker", t);
    renderCompanyDetail();
  }
  $("#co-search-btn").addEventListener("click", doSearch);
  $("#co-search").addEventListener("keydown", function(e){ if (e.key === "Enter") doSearch(); });

  renderCompanyDetail();
  renderCompareChips();
  renderCompareChart();
};

function renderCompanyDetail(){
  var root = $("#co-detail");
  root.innerHTML = "<div class='card'><p class='muted small'>Loading " + esc(CO_TICKER) + "...</p></div>";
  getSeries(CO_TICKER).then(function(s){
    var closes = s.closes, dates = s.dates, volumes = s.volumes;
    var price = closes[closes.length-1];
    var chg = closes.length>1 ? ((price/closes[closes.length-2])-1)*100 : null;
    var window52 = closes.slice(-252);
    var hi52 = Math.max.apply(null, window52), lo52 = Math.min.apply(null, window52);
    var avgVol = volumes.slice(-20).reduce(function(a,b){return a+b;},0) / Math.max(1, volumes.slice(-20).length);
    var rsi = IND.rsi(dates, closes, 14); var rsiVal = rsi[rsi.length-1].p;
    var mfi = IND.mfi(dates, closes, volumes, 14); var mfiVal = mfi[mfi.length-1].p;
    var cmf = IND.cmf(dates, closes, volumes, 21);
    var status = IND.moneyFlowStatus(cmf, 21);
    var ytdIdx = dates.findIndex(function(d){ return d >= (new Date().getFullYear() + "-01-01"); });
    var ytdReturn = ytdIdx > 0 ? ((price/closes[ytdIdx])-1)*100 : null;
    var oneYReturn = closes.length>=252 ? ((price/closes[closes.length-252])-1)*100 : ((price/closes[0])-1)*100;
    var rets = []; for (var i=1;i<closes.length;i++) rets.push(closes[i]/closes[i-1]-1);
    var meanRet = rets.reduce(function(a,b){return a+b;},0)/rets.length;
    var variance = rets.reduce(function(a,b){return a+Math.pow(b-meanRet,2);},0)/rets.length;
    var annVol = Math.sqrt(variance*252)*100;

    root.innerHTML =
      "<div class='card'>" +
        "<div class='flex-between'>" +
          "<div><h2>" + esc(CO_TICKER) + (s.synthetic ? " <span class='tag'>sample data</span>" : "") + "</h2><p class='muted small'>" + esc(tickerName(CO_TICKER)) + "</p></div>" +
          "<div style='text-align:right'><div style='font-size:26px;font-weight:800'>" + fmtPrice(price) + "</div><div class='" + pctClass(chg) + "'>" + fmtPct(chg) + " today</div></div>" +
        "</div>" +
        "<div class='chart-wrap' style='margin-top:14px'><canvas id='co-price-canvas'></canvas></div>" +
        "<div class='section-title'>Key Metrics</div>" +
        "<div class='grid cols-4'>" +
          "<div class='card'><h3>52W Range</h3><div>" + fmtPrice(lo52) + " -- " + fmtPrice(hi52) + "</div></div>" +
          "<div class='card'><h3>Avg Vol (20d)</h3><div>" + Math.round(avgVol).toLocaleString() + "</div></div>" +
          "<div class='card'><h3>RSI(14) / MFI(14)</h3><div>" + fmtNum(rsiVal,1) + " / " + fmtNum(mfiVal,1) + "</div></div>" +
          "<div class='card'><h3>Money Flow</h3><div><span class='pill " + status.cls + "'>" + status.label + "</span></div></div>" +
          "<div class='card'><h3>YTD Return</h3><div class='" + pctClass(ytdReturn) + "'>" + fmtPct(ytdReturn) + "</div></div>" +
          "<div class='card'><h3>1Y Return</h3><div class='" + pctClass(oneYReturn) + "'>" + fmtPct(oneYReturn) + "</div></div>" +
          "<div class='card'><h3>Annualized Vol</h3><div>" + fmtNum(annVol,1) + "%</div></div>" +
          "<div class='card'><h3>Add to List</h3><div><button class='btn small ghost' id='co-add-to-list'>Add " + esc(CO_TICKER) + "</button></div></div>" +
        "</div>" +
      "</div>";

    new Chart($("#co-price-canvas").getContext("2d"), {
      type:"line",
      data:{ labels:dates, datasets:[
        { label:CO_TICKER, data:closes, borderColor:"#4fd1c5", backgroundColor:"rgba(79,209,197,.10)", fill:true, pointRadius:0, borderWidth:1.6, tension:.1 },
        { label:"SMA50", data: IND.sma(dates, closes, 50).map(function(x){return x.p;}), borderColor:"#f6ad55", pointRadius:0, borderWidth:1.2, tension:.1 }
      ]},
      options:{ maintainAspectRatio:false, scales:{ x:{ ticks:{color:"#93a2bb", maxTicksLimit:8}, grid:{color:"#1b2536"} }, y:{ ticks:{color:"#93a2bb"}, grid:{color:"#1b2536"} } }, plugins:{ legend:{ labels:{color:"#93a2bb", boxWidth:12} } } }
    });

    $("#co-add-to-list").addEventListener("click", function(){
      var key = STATE.watchlists.active || Object.keys(STATE.watchlists.lists)[0];
      if (!key) { alert("Create a watchlist first on the Watchlists tab."); return; }
      var list = STATE.watchlists.lists[key];
      if (list.tickers.indexOf(CO_TICKER) === -1) list.tickers.push(CO_TICKER);
      saveWatchlists();
      $("#co-add-to-list").textContent = "Added to " + (list.label||key);
    });
  }).catch(function(e){
    console.error("GMR: company detail failed", e);
    root.innerHTML = "<div class='card'><p class='muted small'>Could not load " + esc(CO_TICKER) + ".</p></div>";
  });
}

function renderCompareChips(){
  var root = $("#co-compare-chips");
  root.innerHTML = CO_COMPARE.map(function(t){
    return "<span class='chip active' data-compare-ticker='" + esc(t) + "'>" + esc(t) + " <span class='x'>x</span></span>";
  }).join("");
  $all("[data-compare-ticker]", root).forEach(function(chip){
    chip.addEventListener("click", function(){
      CO_COMPARE = CO_COMPARE.filter(function(t){ return t !== chip.dataset.compareTicker; });
      lsSet("companiesCompare", CO_COMPARE);
      renderCompareChips();
      renderCompareChart();
    });
  });
  $("#co-compare-add-btn").onclick = function(){
    var t = ($("#co-compare-add").value||"").trim().toUpperCase();
    if (!t || CO_COMPARE.indexOf(t) !== -1) return;
    CO_COMPARE.push(t);
    lsSet("companiesCompare", CO_COMPARE);
    $("#co-compare-add").value = "";
    renderCompareChips();
    renderCompareChart();
  };
}

function renderCompareChart(){
  var canvas = $("#co-compare-canvas");
  var tableRoot = $("#co-compare-table");
  if (!CO_COMPARE.length){ canvas.getContext("2d").clearRect(0,0,canvas.width,canvas.height); tableRoot.innerHTML=""; return; }
  var colors = ["#4fd1c5","#f6ad55","#5b8cff","#3ecf8e","#f56565","#a78bfa","#f472b6"];
  Promise.all(CO_COMPARE.map(function(t){ return getSeries(t); })).then(function(seriesList){
    var maxLen = Math.max.apply(null, seriesList.map(function(s){ return s.dates.length; }));
    var baseDates = seriesList.filter(function(s){ return s.dates.length===maxLen; })[0].dates;
    var datasets = seriesList.map(function(s, i){
      var offset = baseDates.length - s.closes.length;
      var rebased = baseDates.map(function(d, idx){
        var si = idx - offset;
        if (si < 0) return null;
        return (s.closes[si]/s.closes[0])*100;
      });
      return { label:CO_COMPARE[i], data:rebased, borderColor:colors[i%colors.length], pointRadius:0, borderWidth:1.5, tension:.1 };
    });
    new Chart(canvas.getContext("2d"), {
      type:"line", data:{ labels:baseDates, datasets:datasets },
      options:{ maintainAspectRatio:false, scales:{ x:{ ticks:{color:"#93a2bb", maxTicksLimit:8}, grid:{color:"#1b2536"} }, y:{ ticks:{color:"#93a2bb"}, grid:{color:"#1b2536"} } }, plugins:{ legend:{ labels:{color:"#93a2bb", boxWidth:12} } } }
    });
    var html = "<table><thead><tr><th>Ticker</th><th>Price</th><th>1Y Return</th></tr></thead><tbody>";
    seriesList.forEach(function(s, i){
      var price = s.closes[s.closes.length-1];
      var ret = s.closes.length>=252 ? ((price/s.closes[s.closes.length-252])-1)*100 : ((price/s.closes[0])-1)*100;
      html += "<tr><td>" + esc(CO_COMPARE[i]) + "</td><td>" + fmtPrice(price) + "</td><td class='" + pctClass(ret) + "'>" + fmtPct(ret) + "</td></tr>";
    });
    html += "</tbody></table>";
    tableRoot.innerHTML = html;
  }).catch(function(e){ console.error("GMR: compare chart failed", e); });
}
"""

JS_OPTIMIZER = r"""
// ---- Optimizer tab ---------------------------------------------------
var OPT_CAP = lsGet("optCap", 0.20);
var OPT_UNIVERSE_KEY = null;
var OPT_SELECTED = null; // {vol, ret, weights, tickers}
var OPT_SAMPLES = null;

function optUniverseTickers(){
  var key = STATE.watchlists.active;
  var list = key && STATE.watchlists.lists[key];
  if (list && list.tickers.length >= 2) { OPT_UNIVERSE_KEY = key; return list.tickers; }
  OPT_UNIVERSE_KEY = "nuclear (default)";
  return STATE.constituents.map(function(c){ return c.ticker; });
}

function dailyReturns(closes){
  var r = []; for (var i=1;i<closes.length;i++) r.push(closes[i]/closes[i-1]-1);
  return r;
}
function mean(arr){ return arr.reduce(function(a,b){return a+b;},0)/arr.length; }
function covMatrix(returnsMatrix){
  var n = returnsMatrix.length, m = returnsMatrix[0].length;
  var means = returnsMatrix.map(mean);
  var cov = [];
  for (var i=0;i<n;i++){
    cov.push([]);
    for (var j=0;j<n;j++){
      var s = 0;
      for (var t=0;t<m;t++) s += (returnsMatrix[i][t]-means[i])*(returnsMatrix[j][t]-means[j]);
      cov[i].push(s/m);
    }
  }
  return cov;
}
function applyCapAndRenormalize(weights, cap){
  var w = weights.slice();
  for (var iter=0; iter<20; iter++){
    var over = w.map(function(x){ return x>cap; });
    if (!over.some(Boolean)) break;
    var excess = 0;
    for (var i=0;i<w.length;i++){ if (over[i]){ excess += w[i]-cap; w[i]=cap; } }
    var freeIdx = []; for (i=0;i<w.length;i++) if (!over[i]) freeIdx.push(i);
    var freeSum = freeIdx.reduce(function(a,i){return a+w[i];},0);
    if (!freeIdx.length || freeSum<=0) break;
    freeIdx.forEach(function(i){ w[i] += excess * (w[i]/freeSum); });
  }
  var total = w.reduce(function(a,b){return a+b;},0);
  return w.map(function(x){ return x/total; });
}
function randomWeights(n){
  var raw = []; for (var i=0;i<n;i++) raw.push(-Math.log(Math.random()));
  var sum = raw.reduce(function(a,b){return a+b;},0);
  return raw.map(function(x){ return x/sum; });
}
function portfolioStats(w, meanRet, cov, rf){
  var ret = 0; for (var i=0;i<w.length;i++) ret += w[i]*meanRet[i];
  var variance = 0;
  for (i=0;i<w.length;i++) for (var j=0;j<w.length;j++) variance += w[i]*w[j]*cov[i][j];
  var vol = Math.sqrt(Math.max(0,variance));
  var sharpe = vol>0 ? (ret-rf)/vol : 0;
  return {ret:ret, vol:vol, sharpe:sharpe};
}

RENDERERS.optimizer = function(root){
  var tickers = optUniverseTickers();
  root.innerHTML =
    "<div class='card'>" +
      "<h2>Optimizer</h2>" +
      "<p class='muted small'>Universe: <b>" + esc(OPT_UNIVERSE_KEY) + "</b> (" + tickers.length + " names, from your active watchlist). Switch watchlists on the Watchlists tab to optimize a different basket.</p>" +
      "<div class='row'><label style='margin:0'>Max position size:</label>" +
        "<span class='chip" + (OPT_CAP===0.15?" active":"") + "' data-cap='0.15'>15%</span>" +
        "<span class='chip" + (OPT_CAP===0.20?" active":"") + "' data-cap='0.20'>20%</span>" +
        "<span class='chip" + (OPT_CAP===0.25?" active":"") + "' data-cap='0.25'>25%</span>" +
      "</div>" +
      "<div class='row' style='margin-top:8px'>" +
        "<button class='btn small' data-objective='sharpe'>Max Sharpe</button>" +
        "<button class='btn small secondary' data-objective='minvol'>Min Vol</button>" +
        "<button class='btn small secondary' data-objective='equal'>Equal Weight</button>" +
        "<button class='btn small secondary' data-objective='invvol'>Inverse Vol</button>" +
      "</div>" +
    "</div>" +
    "<div class='card'>" +
      "<h3>Efficient Frontier</h3>" +
      "<p class='muted small'>Click anywhere on the frontier to snap to that mix and rebuild the weights table.</p>" +
      "<div class='chart-wrap'><canvas id='opt-frontier-canvas'></canvas></div>" +
    "</div>" +
    "<div class='card' id='opt-weights-card'></div>";

  $all("[data-cap]", root).forEach(function(b){
    b.addEventListener("click", function(){ OPT_CAP = parseFloat(b.dataset.cap); lsSet("optCap", OPT_CAP); OPT_SAMPLES=null; showTab("optimizer"); });
  });

  runOptimizer(tickers).then(function(){
    $all("[data-objective]", root).forEach(function(b){
      b.addEventListener("click", function(){ selectByObjective(b.dataset.objective); });
    });
    selectByObjective("sharpe");
  });
};

function runOptimizer(tickers){
  return Promise.all(tickers.map(function(t){ return getSeries(t); })).then(function(seriesList){
    var minLen = Math.min.apply(null, seriesList.map(function(s){ return s.closes.length; }));
    var returnsMatrix = seriesList.map(function(s){ return dailyReturns(s.closes.slice(-minLen)); });
    var meanRet = returnsMatrix.map(function(r){ return mean(r)*252; });
    var cov = covMatrix(returnsMatrix).map(function(row){ return row.map(function(v){ return v*252; }); });
    var n = tickers.length;
    var rf = 0.04;
    var samples = [];
    var N = 2500;
    for (var s=0; s<N; s++){
      var w = applyCapAndRenormalize(randomWeights(n), OPT_CAP);
      var stats = portfolioStats(w, meanRet, cov, rf);
      samples.push({weights:w, ret:stats.ret, vol:stats.vol, sharpe:stats.sharpe});
    }
    // named strategies
    var equalW = applyCapAndRenormalize(tickers.map(function(){ return 1/n; }), OPT_CAP);
    var vols = tickers.map(function(_,i){ return Math.sqrt(cov[i][i]); });
    var invVolRaw = vols.map(function(v){ return v>0 ? 1/v : 0; });
    var invVolSum = invVolRaw.reduce(function(a,b){return a+b;},0);
    var invVolW = applyCapAndRenormalize(invVolRaw.map(function(v){ return v/invVolSum; }), OPT_CAP);
    var bestSharpe = samples.reduce(function(a,b){ return b.sharpe>a.sharpe ? b : a; });
    var bestMinVol = samples.reduce(function(a,b){ return b.vol<a.vol ? b : a; });
    OPT_SAMPLES = {
      tickers: tickers, meanRet: meanRet, cov: cov, rf: rf, samples: samples,
      named: {
        sharpe: bestSharpe,
        minvol: bestMinVol,
        equal: {weights:equalW, ret:portfolioStats(equalW,meanRet,cov,rf).ret, vol:portfolioStats(equalW,meanRet,cov,rf).vol, sharpe:portfolioStats(equalW,meanRet,cov,rf).sharpe},
        invvol: {weights:invVolW, ret:portfolioStats(invVolW,meanRet,cov,rf).ret, vol:portfolioStats(invVolW,meanRet,cov,rf).vol, sharpe:portfolioStats(invVolW,meanRet,cov,rf).sharpe}
      }
    };
    renderFrontierChart();
  }).catch(function(e){
    console.error("GMR: optimizer failed", e);
    $("#opt-weights-card").innerHTML = "<p class='muted small'>Could not compute the optimizer right now.</p>";
  });
}

var OPT_CHART = null;
function renderFrontierChart(){
  var canvas = $("#opt-frontier-canvas");
  var cloud = OPT_SAMPLES.samples.map(function(s){ return {x:s.vol*100, y:s.ret*100}; });
  // frontier boundary: best return per vol bucket
  var buckets = {};
  OPT_SAMPLES.samples.forEach(function(s){
    var key = Math.round(s.vol*200); // 0.5% bins
    if (!buckets[key] || s.ret > buckets[key].ret) buckets[key] = s;
  });
  var frontier = Object.keys(buckets).map(function(k){ return buckets[k]; }).sort(function(a,b){ return a.vol-b.vol; });
  var frontierPoints = frontier.map(function(s){ return {x:s.vol*100, y:s.ret*100}; });

  if (OPT_CHART) OPT_CHART.destroy();
  OPT_CHART = new Chart(canvas.getContext("2d"), {
    type:"scatter",
    data:{ datasets:[
      { label:"Sampled portfolios", data:cloud, backgroundColor:"rgba(91,140,255,.25)", pointRadius:2 },
      { label:"Efficient frontier", data:frontierPoints, showLine:true, borderColor:"#4fd1c5", backgroundColor:"transparent", pointRadius:0, borderWidth:2 },
      { label:"Selected mix", data:[], backgroundColor:"#f6ad55", pointRadius:7, pointHoverRadius:8 }
    ]},
    options:{
      maintainAspectRatio:false,
      scales:{ x:{ title:{display:true,text:"Annualized Volatility %",color:"#93a2bb"}, ticks:{color:"#93a2bb"}, grid:{color:"#1b2536"} },
               y:{ title:{display:true,text:"Annualized Return %",color:"#93a2bb"}, ticks:{color:"#93a2bb"}, grid:{color:"#1b2536"} } },
      plugins:{ legend:{ labels:{color:"#93a2bb", boxWidth:12} } },
      onClick: function(evt){
        var pts = OPT_CHART.getElementsAtEventForMode(evt, "nearest", {intersect:false}, true);
        if (!pts.length) return;
        var dsIndex = pts[0].datasetIndex;
        if (dsIndex === 2) return;
        var idx = pts[0].index;
        var pool = dsIndex === 1 ? frontier : OPT_SAMPLES.samples;
        var chosen = pool[idx];
        if (chosen) selectPortfolio(chosen);
      }
    }
  });
}

function selectByObjective(key){
  var named = OPT_SAMPLES.named[key];
  selectPortfolio(named);
  $all("[data-objective]", document).forEach(function(b){
    b.className = "btn small" + (b.dataset.objective===key ? "" : " secondary");
  });
}

function selectPortfolio(p){
  OPT_SELECTED = p;
  OPT_CHART.data.datasets[2].data = [{x:p.vol*100, y:p.ret*100}];
  OPT_CHART.update();
  renderWeightsTable(p);
}

function renderWeightsTable(p){
  var root = $("#opt-weights-card");
  var tickers = OPT_SAMPLES.tickers;
  var rows = tickers.map(function(t,i){ return {ticker:t, weight:p.weights[i]}; }).sort(function(a,b){ return b.weight-a.weight; });
  var html = "<h3>Weights for Selected Mix</h3>" +
    "<div class='grid cols-3' style='margin-bottom:14px'>" +
      "<div class='card'><h3>Expected Return</h3><div class='" + pctClass(p.ret*100) + "'>" + fmtPct(p.ret*100) + "</div></div>" +
      "<div class='card'><h3>Volatility</h3><div>" + fmtNum(p.vol*100,1) + "%</div></div>" +
      "<div class='card'><h3>Sharpe</h3><div>" + fmtNum(p.sharpe,2) + "</div></div>" +
    "</div>" +
    "<table><thead><tr><th>Ticker</th><th>Weight</th></tr></thead><tbody>";
  rows.forEach(function(r){
    if (r.weight < 0.001) return;
    html += "<tr><td>" + esc(r.ticker) + "</td><td>" + fmtNum(r.weight*100,1) + "%</td></tr>";
  });
  html += "</tbody></table>";
  root.innerHTML = html;
}
"""

JS_BACKTEST = r"""
// ---- Backtest tab ---------------------------------------------------
var BT_LOOKBACK = lsGet("btLookback", "1Y");
var BT_BENCH = lsGet("btBench", {SPY:true, URA:true, NLR:true});
var BT_OVERLAYS = lsGet("btOverlays", {drawdown:false, sharpe:false});
var LOOKBACK_YEARS = {"1Y":1, "2Y":2, "3Y":3, "5Y":5, "10Y":10, "Max":40};
var BT_CHARTS = {};

RENDERERS.backtest = function(root){
  root.innerHTML =
    "<div class='card'>" +
      "<h2>Backtest</h2>" +
      "<p class='muted small'>Composite is the featured Nuclear index (weighted by constituent). Benchmarks: SPY (S&amp;P 500), URA (uranium miners ETF), NLR (uranium + nuclear energy ETF).</p>" +
      "<div class='row'><label style='margin:0'>Lookback:</label>" +
        Object.keys(LOOKBACK_YEARS).map(function(k){ return "<span class='chip" + (BT_LOOKBACK===k?" active":"") + "' data-lookback='" + k + "'>" + k + "</span>"; }).join("") +
      "</div>" +
      "<div class='row' style='margin-top:8px'><label style='margin:0'>Benchmarks:</label>" +
        Object.keys(BT_BENCH).map(function(k){ return "<span class='chip" + (BT_BENCH[k]?" active":"") + "' data-bench='" + k + "'>" + k + "</span>"; }).join("") +
      "</div>" +
      "<div class='row' style='margin-top:8px'>" +
        "<span class='chip" + (BT_OVERLAYS.drawdown?" active":"") + "' data-overlay='drawdown'>Rolling Drawdown</span>" +
        "<span class='chip" + (BT_OVERLAYS.sharpe?" active":"") + "' data-overlay='sharpe'>Rolling 63d Sharpe</span>" +
      "</div>" +
    "</div>" +
    "<div class='card'><h3>Composite vs Benchmarks</h3><div class='chart-wrap'><canvas id='bt-perf-canvas'></canvas></div><div id='bt-stats'></div></div>" +
    "<div id='bt-overlay-panels'></div>";

  $all("[data-lookback]", root).forEach(function(b){
    b.addEventListener("click", function(){ BT_LOOKBACK = b.dataset.lookback; lsSet("btLookback", BT_LOOKBACK); showTab("backtest"); });
  });
  $all("[data-bench]", root).forEach(function(b){
    b.addEventListener("click", function(){ BT_BENCH[b.dataset.bench] = !BT_BENCH[b.dataset.bench]; lsSet("btBench", BT_BENCH); showTab("backtest"); });
  });
  $all("[data-overlay]", root).forEach(function(b){
    b.addEventListener("click", function(){ BT_OVERLAYS[b.dataset.overlay] = !BT_OVERLAYS[b.dataset.overlay]; lsSet("btOverlays", BT_OVERLAYS); showTab("backtest"); });
  });

  runBacktest();
};

function cutoffDate(years){
  var d = new Date(); d.setFullYear(d.getFullYear() - years);
  return d.toISOString().slice(0,10);
}

function runBacktest(){
  var cons = STATE.constituents;
  var benchTickers = Object.keys(BT_BENCH).filter(function(k){ return BT_BENCH[k]; });
  var allTickers = cons.map(function(c){ return c.ticker; }).concat(benchTickers);
  var range = LOOKBACK_YEARS[BT_LOOKBACK] > 8 ? "max" : (LOOKBACK_YEARS[BT_LOOKBACK] >= 5 ? "10y" : "2y");

  Promise.all(allTickers.map(function(t){ return getSeries(t, range); })).then(function(seriesList){
    var cutoff = BT_LOOKBACK === "Max" ? "1900-01-01" : cutoffDate(LOOKBACK_YEARS[BT_LOOKBACK]);
    var conSeries = seriesList.slice(0, cons.length).map(function(s){ return trimSeries(s, cutoff); });
    var benchSeries = {};
    benchTickers.forEach(function(t, i){ benchSeries[t] = trimSeries(seriesList[cons.length+i], cutoff); });

    var baseDates = conSeries.reduce(function(longest, s){ return s.dates.length > longest.length ? s.dates : longest; }, []);
    var totalWeight = cons.reduce(function(a,c){ return a+c.weight; }, 0);
    var composite = baseDates.map(function(d, i){
      var sum=0, wsum=0;
      conSeries.forEach(function(s, idx){
        var si = i - (baseDates.length - s.dates.length);
        if (si < 0 || !s.closes.length) return;
        var base = s.closes[0];
        var val = s.closes[si] != null ? s.closes[si] : s.closes[s.closes.length-1];
        sum += (val/base)*100 * cons[idx].weight; wsum += cons[idx].weight;
      });
      return wsum ? sum/wsum : null;
    });

    var datasets = [{ label:"GMR Nuclear Composite", data:composite, borderColor:"#4fd1c5", backgroundColor:"rgba(79,209,197,.1)", fill:true, pointRadius:0, borderWidth:2, tension:.1 }];
    var colors = {SPY:"#f6ad55", URA:"#5b8cff", NLR:"#a78bfa"};
    benchTickers.forEach(function(t){
      var s = benchSeries[t];
      var offset = baseDates.length - s.dates.length;
      var rebased = baseDates.map(function(d, idx){
        var si = idx - offset;
        if (si < 0 || si >= s.closes.length) return null;
        return (s.closes[si]/s.closes[0])*100;
      });
      datasets.push({ label:t, data:rebased, borderColor:colors[t]||"#e7edf7", pointRadius:0, borderWidth:1.5, tension:.1 });
    });

    if (BT_CHARTS.perf) BT_CHARTS.perf.destroy();
    BT_CHARTS.perf = new Chart($("#bt-perf-canvas").getContext("2d"), {
      type:"line", data:{ labels:baseDates, datasets:datasets },
      options:{ maintainAspectRatio:false, scales:{ x:{ ticks:{color:"#93a2bb", maxTicksLimit:8}, grid:{color:"#1b2536"} }, y:{ ticks:{color:"#93a2bb"}, grid:{color:"#1b2536"} } }, plugins:{ legend:{ labels:{color:"#93a2bb", boxWidth:12} } } }
    });

    renderBacktestStats(composite, benchSeries, baseDates);
    renderOverlayPanels(baseDates, composite);
  }).catch(function(e){
    console.error("GMR: backtest failed", e);
    $("#bt-perf-canvas").parentElement.innerHTML = "<p class='muted small'>Could not run the backtest right now.</p>";
  });
}

function trimSeries(s, cutoff){
  var startIdx = s.dates.findIndex(function(d){ return d >= cutoff; });
  if (startIdx <= 0) return s;
  return { dates:s.dates.slice(startIdx), closes:s.closes.slice(startIdx), volumes:s.volumes.slice(startIdx), synthetic:s.synthetic };
}

function totalReturn(series){ return series.length>1 ? (series[series.length-1]/series[0]-1)*100 : null; }

function renderBacktestStats(composite, benchSeries, baseDates){
  var root = $("#bt-stats");
  var validComposite = composite.filter(function(v){ return v!=null; });
  var html = "<div class='section-title'>Total Return Over Period</div><div class='grid cols-4'>" +
    "<div class='card'><h3>Composite</h3><div class='" + pctClass(totalReturn(validComposite)) + "'>" + fmtPct(totalReturn(validComposite)) + "</div></div>";
  Object.keys(benchSeries).forEach(function(t){
    var closes = benchSeries[t].closes;
    html += "<div class='card'><h3>" + esc(t) + "</h3><div class='" + pctClass(totalReturn(closes)) + "'>" + fmtPct(totalReturn(closes)) + "</div></div>";
  });
  html += "</div>";
  root.innerHTML = html;
}

function rollingDrawdown(series){
  var out = []; var peak = -Infinity;
  for (var i=0;i<series.length;i++){
    if (series[i]==null){ out.push(null); continue; }
    peak = Math.max(peak, series[i]);
    out.push(((series[i]/peak)-1)*100);
  }
  return out;
}
function rollingSharpe(series, window){
  window = window || 63;
  var rets = [null];
  for (var i=1;i<series.length;i++) rets.push(series[i]!=null && series[i-1]!=null ? series[i]/series[i-1]-1 : null);
  var out = [];
  for (i=0;i<series.length;i++){
    if (i+1 < window){ out.push(null); continue; }
    var win = rets.slice(i-window+1, i+1).filter(function(v){ return v!=null; });
    if (win.length < window*0.8){ out.push(null); continue; }
    var m = mean(win);
    var variance = win.reduce(function(a,b){ return a+Math.pow(b-m,2); },0)/win.length;
    var sd = Math.sqrt(variance);
    out.push(sd>0 ? (m/sd)*Math.sqrt(252) : null);
  }
  return out;
}

function renderOverlayPanels(dates, composite){
  var root = $("#bt-overlay-panels");
  root.innerHTML = "";
  if (BT_OVERLAYS.drawdown){
    var card = document.createElement("div"); card.className = "card";
    card.innerHTML = "<h3>Rolling Drawdown (Composite)</h3><div class='chart-wrap small'><canvas id='bt-dd-canvas'></canvas></div>";
    root.appendChild(card);
    var dd = rollingDrawdown(composite);
    if (BT_CHARTS.dd) BT_CHARTS.dd.destroy();
    BT_CHARTS.dd = new Chart($("#bt-dd-canvas").getContext("2d"), {
      type:"line", data:{ labels:dates, datasets:[{ label:"Drawdown %", data:dd, borderColor:"#f56565", backgroundColor:"rgba(245,101,101,.15)", fill:true, pointRadius:0, borderWidth:1.3 }] },
      options:{ maintainAspectRatio:false, scales:{ x:{ ticks:{color:"#93a2bb", maxTicksLimit:8}, grid:{color:"#1b2536"} }, y:{ ticks:{color:"#93a2bb"}, grid:{color:"#1b2536"} } }, plugins:{ legend:{ labels:{color:"#93a2bb", boxWidth:12} } } }
    });
  }
  if (BT_OVERLAYS.sharpe){
    var card2 = document.createElement("div"); card2.className = "card";
    card2.innerHTML = "<h3>Rolling 63-Day Sharpe (Composite)</h3><div class='chart-wrap small'><canvas id='bt-sharpe-canvas'></canvas></div>";
    root.appendChild(card2);
    var sh = rollingSharpe(composite, 63);
    if (BT_CHARTS.sharpe) BT_CHARTS.sharpe.destroy();
    BT_CHARTS.sharpe = new Chart($("#bt-sharpe-canvas").getContext("2d"), {
      type:"line", data:{ labels:dates, datasets:[{ label:"Rolling Sharpe", data:sh, borderColor:"#5b8cff", pointRadius:0, borderWidth:1.3 }] },
      options:{ maintainAspectRatio:false, scales:{ x:{ ticks:{color:"#93a2bb", maxTicksLimit:8}, grid:{color:"#1b2536"} }, y:{ ticks:{color:"#93a2bb"}, grid:{color:"#1b2536"} } }, plugins:{ legend:{ labels:{color:"#93a2bb", boxWidth:12} } } }
    });
  }
}
"""

JS_UPDATES = r"""
// ---- Updates tab (catalyst calendar + news feed) ----------------------
var UP_TYPE = "all";
var UP_TICKER = "all";

RENDERERS.updates = function(root){
  var items = (STATE.catalysts||[]).slice().sort(function(a,b){ return b.date < a.date ? -1 : (b.date > a.date ? 1 : 0); });
  var tickers = Array.from(new Set(items.map(function(i){ return i.ticker; }))).sort();

  root.innerHTML =
    "<div class='card'>" +
      "<h2>Updates</h2>" +
      "<p class='muted small'>Catalyst calendar and news, merged and sorted newest-first.</p>" +
      "<div class='row'>" +
        "<span class='chip" + (UP_TYPE==="all"?" active":"") + "' data-type='all'>All</span>" +
        "<span class='chip" + (UP_TYPE==="catalyst"?" active":"") + "' data-type='catalyst'>Catalysts</span>" +
        "<span class='chip" + (UP_TYPE==="news"?" active":"") + "' data-type='news'>News</span>" +
        "<select id='up-ticker-select' style='width:160px;margin-left:10px'>" +
          "<option value='all'>All tickers</option>" +
          tickers.map(function(t){ return "<option value='" + esc(t) + "'" + (t===UP_TICKER?" selected":"") + ">" + esc(t) + "</option>"; }).join("") +
        "</select>" +
      "</div>" +
    "</div>" +
    "<div class='card' id='up-feed'></div>";

  $all("[data-type]", root).forEach(function(b){
    b.addEventListener("click", function(){ UP_TYPE = b.dataset.type; showTab("updates"); });
  });
  $("#up-ticker-select").addEventListener("change", function(e){ UP_TICKER = e.target.value; renderUpdatesFeed(items); });

  renderUpdatesFeed(items);
};

function renderUpdatesFeed(items){
  var root = $("#up-feed");
  var filtered = items.filter(function(i){
    if (UP_TYPE !== "all" && i.type !== UP_TYPE) return false;
    if (UP_TICKER !== "all" && i.ticker !== UP_TICKER) return false;
    return true;
  });
  if (!filtered.length){ root.innerHTML = "<p class='muted small'>No items match this filter.</p>"; return; }
  root.innerHTML = filtered.map(function(i){
    var isFuture = i.date >= todayISO();
    return "<div class='row' style='padding:10px 0;border-bottom:1px solid var(--border);align-items:flex-start'>" +
      "<span class='pill" + (i.type==="catalyst" ? (isFuture ? " up" : "") : "") + "'>" + (i.type==="catalyst"?"Catalyst":"News") + "</span>" +
      "<div style='flex:1;min-width:200px'>" +
        "<div><b>" + esc(i.title) + "</b> <span class='tag'>" + esc(i.ticker) + "</span></div>" +
        "<div class='muted small'>" + esc(i.date) + " -- " + esc(i.summary||"") + "</div>" +
      "</div>" +
    "</div>";
  }).join("");
}
"""

JS_PREIPO = r"""
// ---- Pre-IPO tab -------------------------------------------------------
RENDERERS.preipo = function(root){
  var items = STATE.preIpo || [];
  root.innerHTML =
    "<div class='card'>" +
      "<h2>Pre-IPO Watchlist</h2>" +
      "<p class='muted small'>Private companies worth tracking ahead of a potential listing. Status reflects public reporting and can change quickly.</p>" +
    "</div>" +
    "<div class='grid cols-2'>" +
      items.map(function(c){
        return "<div class='card'>" +
          "<div class='flex-between'><h3 style='margin:0;color:var(--text);text-transform:none;font-size:16px'>" + esc(c.name) + "</h3><span class='tag " + esc(c.status) + "'>" + esc(c.status) + "</span></div>" +
          "<div class='muted small' style='margin-top:4px'>" + esc(c.sector) + "</div>" +
          "<p class='small' style='margin-top:8px'>" + esc(c.desc) + "</p>" +
        "</div>";
      }).join("") +
    "</div>";
};
"""

JS_PROFILE = r"""
// ---- Profile tab + NL quick command bar --------------------------------
var NL_HELP_MESSAGE =
  "I did not catch a change in that. Here is exactly what I can do:<br>" +
  "<b>Build a watchlist</b> -- try \"build me a watchlist for semiconductors\" or \"help me track neuro stocks\".<br>" +
  "<b>Tweak your portfolio profile</b> -- mention any of: capital $10000, max position 20%, min position 5%, " +
  "hold 6 to 10 names, target vol 20%, max drawdown 25%, exclude TSLA, require NVDA, objective max-sharpe " +
  "(or min-vol / aggressive).";

RENDERERS.profile = function(root){
  root.innerHTML =
    "<div class='card'>" +
      "<h2>Quick Command Bar</h2>" +
      "<p class='muted small'>Plain-English shortcuts -- no AI involved, just pattern matching against known intents.</p>" +
      "<div class='row'><input id='nl-input' type='text' placeholder='e.g. build me a watchlist for cybersecurity' style='flex:1;min-width:260px'><button class='btn' id='nl-run'>Run</button></div>" +
      "<div id='nl-output' class='footer-note'></div>" +
    "</div>" +
    "<div id='pf-form-wrap'></div>";

  $("#nl-run").addEventListener("click", runNLCommand);
  $("#nl-input").addEventListener("keydown", function(e){ if (e.key==="Enter") runNLCommand(); });
  renderProfileForm();
};

function renderProfileForm(){
  var root = $("#pf-form-wrap");
  var p = STATE.profile;
  root.innerHTML =
    "<div class='card'>" +
      "<h2>Risk Profile</h2>" +
      "<div class='grid cols-2'>" +
        "<div><label>Capital ($)</label><input id='pf-capital' type='number' value='" + p.capital + "'></div>" +
        "<div><label>Objective</label><select id='pf-objective'>" +
          ["max-sharpe","min-vol","aggressive"].map(function(o){ return "<option value='" + o + "'" + (p.objective===o?" selected":"") + ">" + o + "</option>"; }).join("") +
        "</select></div>" +
        "<div><label>Max position size (%)</label><input id='pf-maxpos' type='number' value='" + p.maxPosition + "'></div>" +
        "<div><label>Min position size (%)</label><input id='pf-minpos' type='number' value='" + p.minPosition + "'></div>" +
        "<div><label>Hold min names</label><input id='pf-holdmin' type='number' value='" + p.holdMin + "'></div>" +
        "<div><label>Hold max names</label><input id='pf-holdmax' type='number' value='" + p.holdMax + "'></div>" +
        "<div><label>Target volatility (%)</label><input id='pf-targetvol' type='number' value='" + p.targetVol + "'></div>" +
        "<div><label>Max drawdown (%)</label><input id='pf-maxdd' type='number' value='" + p.maxDrawdown + "'></div>" +
        "<div><label>Exclude tickers (comma-separated)</label><input id='pf-exclude' type='text' value='" + esc((p.exclude||[]).join(", ")) + "'></div>" +
        "<div><label>Require tickers (comma-separated)</label><input id='pf-require' type='text' value='" + esc((p.require||[]).join(", ")) + "'></div>" +
      "</div>" +
      "<div class='cta-row'><button class='btn' id='pf-save'>Save profile</button><span id='pf-saved' class='footer-note'></span></div>" +
    "</div>";

  $("#pf-save").addEventListener("click", function(){
    STATE.profile.capital = parseFloat($("#pf-capital").value) || 0;
    STATE.profile.objective = $("#pf-objective").value;
    STATE.profile.maxPosition = parseFloat($("#pf-maxpos").value) || 0;
    STATE.profile.minPosition = parseFloat($("#pf-minpos").value) || 0;
    STATE.profile.holdMin = parseInt($("#pf-holdmin").value) || 0;
    STATE.profile.holdMax = parseInt($("#pf-holdmax").value) || 0;
    STATE.profile.targetVol = parseFloat($("#pf-targetvol").value) || 0;
    STATE.profile.maxDrawdown = parseFloat($("#pf-maxdd").value) || 0;
    STATE.profile.exclude = ($("#pf-exclude").value||"").split(",").map(function(s){return s.trim().toUpperCase();}).filter(Boolean);
    STATE.profile.require = ($("#pf-require").value||"").split(",").map(function(s){return s.trim().toUpperCase();}).filter(Boolean);
    saveProfile();
    $("#pf-saved").textContent = "Saved.";
  });
}

function findPresetByPhrase(phrase){
  phrase = phrase.toLowerCase().trim().replace(/\bstocks?\b/g,"").replace(/\bshares?\b/g,"").trim();
  if (!phrase) return null;
  var best = null;
  STATE.presets.forEach(function(p){
    var aliases = (p.aliases||[]).concat([p.label.toLowerCase()]);
    aliases.forEach(function(a){
      if (phrase.indexOf(a) !== -1 || a.indexOf(phrase) !== -1) {
        if (!best || a.length > best.matchLen) best = {preset:p, matchLen:a.length};
      }
    });
  });
  return best ? best.preset : null;
}

function tryWatchlistIntent(text){
  var patterns = [
    /build (?:me )?a watchlist for (.+)/i,
    /create (?:me )?a watchlist for (.+)/i,
    /help me track (.+)/i,
    /track (.+)/i,
    /watchlist (?:for|of) (.+)/i
  ];
  for (var i=0;i<patterns.length;i++){
    var m = text.match(patterns[i]);
    if (m){
      var preset = findPresetByPhrase(m[1]);
      if (preset){
        STATE.watchlists.lists[preset.key] = { label:preset.label, desc:preset.desc, tickers:preset.tickers.slice(), indicators: Object.assign({}, DEFAULT_INDICATORS) };
        STATE.watchlists.active = preset.key;
        saveWatchlists();
        return "Built the <b>" + esc(preset.label) + "</b> watchlist (" + preset.tickers.length + " names). Open the Watchlists tab to see it.";
      }
      return null;
    }
  }
  return null;
}

var NL_STOPWORDS = "(?:and|be|is|the|for|with|target|vol(?:atility)?|max(?:imum)?|min(?:imum)?|hold|require|exclude|objective|aggressive|names?|position|drawdown|capital|of|to|sharpe)";
function extractTickerList(text, keyword){
  var token = "(?!" + NL_STOPWORDS + "\\b)[a-z]{1,5}";
  var re = new RegExp(keyword + "\\s+(" + token + "(?:\\s*,\\s*" + token + ")*)", "i");
  var m = text.match(re);
  if (!m) return null;
  return m[1].split(",").map(function(s){ return s.trim().toUpperCase(); }).filter(Boolean);
}

function tryPortfolioIntent(text){
  var p = STATE.profile;
  var changes = [];
  var m;
  if ((m = text.match(/capital\s*\$?([\d,]+(?:\.\d+)?)/i))){ p.capital = parseFloat(m[1].replace(/,/g,"")); changes.push("capital -> $" + p.capital); }
  if ((m = text.match(/max(?:imum)? position\s*(?:size)?\s*(?:of|to)?\s*(\d+(?:\.\d+)?)\s*%/i))){ p.maxPosition = parseFloat(m[1]); changes.push("max position -> " + p.maxPosition + "%"); }
  if ((m = text.match(/min(?:imum)? position\s*(?:size)?\s*(?:of|to)?\s*(\d+(?:\.\d+)?)\s*%/i))){ p.minPosition = parseFloat(m[1]); changes.push("min position -> " + p.minPosition + "%"); }
  if ((m = text.match(/hold\s*(\d+)\s*(?:to|-)\s*(\d+)\s*names?/i))){ p.holdMin = parseInt(m[1]); p.holdMax = parseInt(m[2]); changes.push("hold " + p.holdMin + " to " + p.holdMax + " names"); }
  if ((m = text.match(/target vol(?:atility)?\s*(?:of|to)?\s*(\d+(?:\.\d+)?)\s*%/i))){ p.targetVol = parseFloat(m[1]); changes.push("target vol -> " + p.targetVol + "%"); }
  if ((m = text.match(/max(?:imum)? drawdown\s*(?:of|to)?\s*(\d+(?:\.\d+)?)\s*%/i))){ p.maxDrawdown = parseFloat(m[1]); changes.push("max drawdown -> " + p.maxDrawdown + "%"); }
  var ex = extractTickerList(text, "exclude");
  if (ex){
    p.exclude = Array.from(new Set((p.exclude||[]).concat(ex)));
    changes.push("exclude -> " + p.exclude.join(", "));
  }
  var req = extractTickerList(text, "require");
  if (req){
    p.require = Array.from(new Set((p.require||[]).concat(req)));
    changes.push("require -> " + p.require.join(", "));
  }
  if (/aggressive/i.test(text)){ p.objective = "aggressive"; changes.push("objective -> aggressive"); }
  else if (/min[- ]vol/i.test(text)){ p.objective = "min-vol"; changes.push("objective -> min-vol"); }
  else if (/max[- ]sharpe/i.test(text)){ p.objective = "max-sharpe"; changes.push("objective -> max-sharpe"); }

  if (!changes.length) return null;
  saveProfile();
  if ($("#pf-form-wrap")) renderProfileForm();
  return "Updated your profile: " + changes.join("; ") + ".";
}

function runNLCommand(){
  var text = ($("#nl-input").value||"").trim();
  var out = $("#nl-output");
  if (!text){ out.innerHTML = NL_HELP_MESSAGE; return; }
  var result = tryWatchlistIntent(text) || tryPortfolioIntent(text);
  out.innerHTML = result || NL_HELP_MESSAGE;
}
"""

JS_GITHUB = r"""
// ---- GitHub API helpers (used by Alerts + Methodology tabs) -----------
function ghHeaders(){
  return { "Authorization": "token " + STATE.githubToken, "Accept": "application/vnd.github+json" };
}
function ghRepoPath(){ return STATE.githubRepo; } // "owner/repo"
function ghGet(path){
  return fetch("https://api.github.com" + path, { headers: ghHeaders() })
    .then(function(res){ return res.json().then(function(json){ return {ok:res.ok, status:res.status, json:json}; }).catch(function(){ return {ok:res.ok, status:res.status, json:null}; }); });
}
function ghPutFile(filePath, contentObjOrText, message){
  var repo = ghRepoPath();
  var apiPath = "/repos/" + repo + "/contents/" + filePath;
  var text = (typeof contentObjOrText === "string") ? contentObjOrText : JSON.stringify(contentObjOrText, null, 2);
  var b64 = btoa(unescape(encodeURIComponent(text)));
  return ghGet(apiPath).then(function(existing){
    var sha = (existing.ok && existing.json && existing.json.sha) ? existing.json.sha : undefined;
    var body = { message: message, content: b64 };
    if (sha) body.sha = sha;
    return fetch("https://api.github.com" + apiPath, {
      method: "PUT", headers: Object.assign({"Content-Type":"application/json"}, ghHeaders()), body: JSON.stringify(body)
    }).then(function(res){ return res.json().then(function(json){ return {ok:res.ok, status:res.status, json:json}; }); });
  });
}
function ghDispatchWorkflow(workflowFile, inputs){
  var repo = ghRepoPath();
  return fetch("https://api.github.com/repos/" + repo + "/actions/workflows/" + workflowFile + "/dispatches", {
    method: "POST", headers: Object.assign({"Content-Type":"application/json"}, ghHeaders()),
    body: JSON.stringify({ ref: "main", inputs: inputs || {} })
  }).then(function(res){ return {ok:res.ok, status:res.status}; });
}
"""

JS_ALERTS = r"""
// ---- Alerts tab (16 rule types) ----------------------------------------
var RULE_DEFS = [
  {key:"price_above", label:"Price above", fields:[{name:"price", label:"Price ($)", type:"number", def:100}]},
  {key:"price_below", label:"Price below", fields:[{name:"price", label:"Price ($)", type:"number", def:50}]},
  {key:"pct_change", label:"N-day % change", fields:[{name:"days", label:"Days", type:"number", def:5}, {name:"pct", label:"Threshold %", type:"number", def:10}]},
  {key:"pct_change_from_anchor", label:"% change since date", fields:[{name:"anchor", label:"Anchor date", type:"date", def:todayISO()}, {name:"pct", label:"Threshold %", type:"number", def:10}]},
  {key:"rsi_above", label:"RSI above", fields:[{name:"level", label:"RSI level", type:"number", def:70}]},
  {key:"rsi_below", label:"RSI below", fields:[{name:"level", label:"RSI level", type:"number", def:30}]},
  {key:"sma_cross_up", label:"SMA golden cross (50/200 up)", fields:[]},
  {key:"sma_cross_down", label:"SMA death cross (50/200 down)", fields:[]},
  {key:"macd_cross_up", label:"MACD bullish cross", fields:[]},
  {key:"macd_cross_down", label:"MACD bearish cross", fields:[]},
  {key:"volume_spike", label:"Volume spike (x 20d avg)", fields:[{name:"multiplier", label:"Multiplier", type:"number", def:2}]},
  {key:"money_pouring_in", label:"Money pouring in (CMF)", fields:[{name:"threshold", label:"CMF threshold", type:"number", def:0.05}]},
  {key:"distribution_warning", label:"Distribution warning (CMF)", fields:[{name:"threshold", label:"CMF threshold", type:"number", def:0.05}]},
  {key:"mfi_overbought", label:"MFI overbought", fields:[{name:"level", label:"MFI level", type:"number", def:80}]},
  {key:"mfi_oversold", label:"MFI oversold", fields:[{name:"level", label:"MFI level", type:"number", def:20}]},
  {key:"obv_breakout", label:"OBV new N-day high", fields:[{name:"lookback", label:"Lookback (days)", type:"number", def:20}]}
];
var RULE_RECIPES = [
  {label:"RSI Oversold", type:"rsi_below", params:{level:30}},
  {label:"RSI Overbought", type:"rsi_above", params:{level:70}},
  {label:"Golden Cross", type:"sma_cross_up", params:{}},
  {label:"Death Cross", type:"sma_cross_down", params:{}},
  {label:"MACD Bullish Cross", type:"macd_cross_up", params:{}},
  {label:"Volume Spike 2x", type:"volume_spike", params:{multiplier:2}},
  {label:"Money Pouring In", type:"money_pouring_in", params:{threshold:0.05}},
  {label:"Distribution Warning", type:"distribution_warning", params:{threshold:0.05}}
];
var ALERT_FORM = { type:"rsi_below", ticker:"", params:{} };
var SMS_CARRIERS = {
  "": "-- none --", "vtext.com":"Verizon", "txt.att.net":"AT&T", "tmomail.net":"T-Mobile",
  "email.uscc.net":"US Cellular", "sms.cricketwireless.net":"Cricket", "mymetropcs.com":"Metro",
  "sms.myboostmobile.com":"Boost", "msg.fi.google.com":"Google Fi"
};

function ruleDef(type){ return RULE_DEFS.filter(function(r){ return r.key===type; })[0]; }
function ruleSummary(rule){
  var def = ruleDef(rule.type);
  var parts = Object.keys(rule.params||{}).map(function(k){ return k + "=" + rule.params[k]; });
  return (def?def.label:rule.type) + (parts.length ? " (" + parts.join(", ") + ")" : "");
}

RENDERERS.alerts = function(root){
  var a = STATE.alerts;
  root.innerHTML =
    "<div class='card'>" +
      "<h2>Alerts</h2>" +
      "<p class='muted small'>Rule-based alerts evaluated by a GitHub Actions workflow every 15 minutes during US market hours, plus a daily digest.</p>" +
      "<div class='section-title'>Quick Recipes</div>" +
      "<div class='row' id='alert-recipes'></div>" +
      "<div class='section-title'>New Rule</div>" +
      "<div class='grid cols-2'>" +
        "<div><label>Ticker</label><input id='rule-ticker' type='text' placeholder='e.g. CCJ' style='text-transform:uppercase'></div>" +
        "<div><label>Rule type</label><select id='rule-type'>" + RULE_DEFS.map(function(r){ return "<option value='" + r.key + "'" + (r.key===ALERT_FORM.type?" selected":"") + ">" + esc(r.label) + "</option>"; }).join("") + "</select></div>" +
      "</div>" +
      "<div class='grid cols-2' id='rule-param-fields' style='margin-top:6px'></div>" +
      "<div class='cta-row'><button class='btn' id='rule-add-btn'>Add rule</button></div>" +
    "</div>" +
    "<div class='card'><h3>Armed Rules</h3><div id='rules-list'></div></div>" +
    "<div class='card'>" +
      "<h3>Notification Channels</h3>" +
      "<div class='grid cols-2'>" +
        "<div><label>Email</label><input id='chan-email' type='email' value='" + esc((a.channels&&a.channels.email)||"") + "'></div>" +
        "<div><label>Phone number (10 digits)</label><input id='chan-phone' type='text' value='" + esc((a.channels&&a.channels.sms&&a.channels.sms.number)||"") + "'></div>" +
        "<div><label>Carrier (SMS via email gateway)</label><select id='chan-carrier'>" +
          Object.keys(SMS_CARRIERS).map(function(k){ return "<option value='" + k + "'" + ((a.channels&&a.channels.sms&&a.channels.sms.carrier)===k?" selected":"") + ">" + SMS_CARRIERS[k] + "</option>"; }).join("") +
        "</select></div>" +
      "</div>" +
      "<p class='footer-note'>Email-to-SMS gateways are unreliable and carriers can silently drop messages -- treat SMS as best-effort. For guaranteed delivery, a paid provider like Twilio is a natural upgrade path (not implemented here to keep this a $0/month tool).</p>" +
      "<div class='cta-row'><button class='btn secondary' id='chan-save'>Save channels</button><span id='chan-saved' class='footer-note'></span></div>" +
    "</div>" +
    "<div class='card'>" +
      "<h3>Connect GitHub</h3>" +
      "<p class='muted small'>Needed to push alerts.json / watchlists.json and to dispatch the test workflow. Create a token at " +
        "<a href='https://github.com/settings/tokens/new?scopes=repo,workflow&description=GMR' target='_blank' rel='noopener'>github.com/settings/tokens/new</a> with <b>repo</b> and <b>workflow</b> scopes.</p>" +
      "<div class='grid cols-2'>" +
        "<div><label>owner/repo</label><input id='gh-repo' type='text' placeholder='yourname/GMR' value='" + esc(STATE.githubRepo||"") + "'></div>" +
        "<div><label>Personal Access Token</label><input id='gh-token' type='text' placeholder='ghp_...' value='" + esc(STATE.githubToken||"") + "'></div>" +
      "</div>" +
      "<div class='cta-row'><button class='btn secondary' id='gh-save'>Save connection</button><button class='btn' id='arm-btn'>Arm my alerts</button><span id='arm-status' class='footer-note'></span></div>" +
    "</div>" +
    "<div class='card'>" +
      "<h3>Verify Notifications Work</h3>" +
      "<div class='cta-row'>" +
        "<button class='btn' id='test-alert-btn'>Send me a test alert NOW</button>" +
        "<button class='btn secondary' id='diagnose-btn'>Diagnose setup</button>" +
      "</div>" +
      "<div id='diagnose-output' style='margin-top:12px'></div>" +
    "</div>";

  renderRuleRecipes();
  renderRuleParamFields();
  $("#rule-type").addEventListener("change", function(){ ALERT_FORM.type = this.value; ALERT_FORM.params = {}; renderRuleParamFields(); });
  $("#rule-add-btn").addEventListener("click", addRule);
  renderRulesList();

  $("#chan-save").addEventListener("click", function(){
    STATE.alerts.channels = STATE.alerts.channels || {};
    STATE.alerts.channels.email = $("#chan-email").value.trim();
    STATE.alerts.channels.sms = { number: $("#chan-phone").value.trim(), carrier: $("#chan-carrier").value };
    saveAlerts();
    $("#chan-saved").textContent = "Saved.";
  });
  $("#gh-save").addEventListener("click", function(){
    STATE.githubRepo = $("#gh-repo").value.trim();
    STATE.githubToken = $("#gh-token").value.trim();
    lsSet("githubRepo", STATE.githubRepo);
    lsSet("githubToken", STATE.githubToken);
    $("#arm-status").textContent = "Connection saved.";
  });
  $("#arm-btn").addEventListener("click", armAlerts);
  $("#test-alert-btn").addEventListener("click", sendTestAlert);
  $("#diagnose-btn").addEventListener("click", diagnoseSetup);
};

function renderRuleRecipes(){
  var root = $("#alert-recipes");
  root.innerHTML = RULE_RECIPES.map(function(r,i){ return "<span class='chip' data-recipe='" + i + "'>" + esc(r.label) + "</span>"; }).join("");
  $all("[data-recipe]", root).forEach(function(chip){
    chip.addEventListener("click", function(){
      var recipe = RULE_RECIPES[parseInt(chip.dataset.recipe)];
      ALERT_FORM.type = recipe.type;
      ALERT_FORM.params = Object.assign({}, recipe.params);
      $("#rule-type").value = recipe.type;
      renderRuleParamFields();
    });
  });
}

function renderRuleParamFields(){
  var root = $("#rule-param-fields");
  var def = ruleDef(ALERT_FORM.type);
  root.innerHTML = (def.fields||[]).map(function(f){
    var val = (ALERT_FORM.params[f.name] != null) ? ALERT_FORM.params[f.name] : f.def;
    return "<div><label>" + esc(f.label) + "</label><input data-param='" + f.name + "' type='" + f.type + "' value='" + esc(val) + "'></div>";
  }).join("") || "<p class='muted small'>No extra parameters for this rule type.</p>";
  $all("[data-param]", root).forEach(function(inp){
    inp.addEventListener("input", function(){ ALERT_FORM.params[inp.dataset.param] = inp.type==="number" ? parseFloat(inp.value) : inp.value; });
    ALERT_FORM.params[inp.dataset.param] = inp.type==="number" ? parseFloat(inp.value) : inp.value;
  });
}

function addRule(){
  var ticker = ($("#rule-ticker").value||"").trim().toUpperCase();
  if (!ticker){ alert("Enter a ticker first."); return; }
  var rule = { id: uid(), type: ALERT_FORM.type, ticker: ticker, params: Object.assign({}, ALERT_FORM.params), enabled: true };
  STATE.alerts.rules = STATE.alerts.rules || [];
  STATE.alerts.rules.push(rule);
  saveAlerts();
  renderRulesList();
}

function renderRulesList(){
  var root = $("#rules-list");
  var rules = STATE.alerts.rules || [];
  if (!rules.length){ root.innerHTML = "<p class='muted small'>No rules armed yet -- add one above.</p>"; return; }
  root.innerHTML = "<table><thead><tr><th>Ticker</th><th>Rule</th><th>Status</th><th></th></tr></thead><tbody>" +
    rules.map(function(r){
      return "<tr><td>" + esc(r.ticker) + "</td><td>" + esc(ruleSummary(r)) + "</td>" +
        "<td><span class='pill" + (r.enabled?" up":"") + "'>" + (r.enabled?"Armed":"Paused") + "</span></td>" +
        "<td><button class='btn small ghost' data-toggle-rule='" + r.id + "'>" + (r.enabled?"Pause":"Resume") + "</button> " +
        "<button class='btn small ghost' data-remove-rule='" + r.id + "'>Remove</button></td></tr>";
    }).join("") + "</tbody></table>";
  $all("[data-toggle-rule]", root).forEach(function(b){
    b.addEventListener("click", function(){
      var r = STATE.alerts.rules.filter(function(x){ return x.id===b.dataset.toggleRule; })[0];
      if (r){ r.enabled = !r.enabled; saveAlerts(); renderRulesList(); }
    });
  });
  $all("[data-remove-rule]", root).forEach(function(b){
    b.addEventListener("click", function(){
      STATE.alerts.rules = STATE.alerts.rules.filter(function(x){ return x.id!==b.dataset.removeRule; });
      saveAlerts(); renderRulesList();
    });
  });
}

function requireGithubConnection(){
  if (!STATE.githubRepo || !STATE.githubToken){
    alert("Connect GitHub first (owner/repo + Personal Access Token) below.");
    return false;
  }
  return true;
}

function armAlerts(){
  if (!requireGithubConnection()) return;
  var status = $("#arm-status");
  status.textContent = "Pushing alerts.json and watchlists.json...";
  Promise.all([
    ghPutFile("data/alerts.json", STATE.alerts, "GMR: update alerts.json via Alerts tab"),
    ghPutFile("data/watchlists.json", STATE.watchlists, "GMR: update watchlists.json via Alerts tab")
  ]).then(function(results){
    var allOk = results.every(function(r){ return r.ok; });
    status.textContent = allOk ? "Armed! Your rules will run on the next scheduled workflow tick." : "Something failed -- check the token scopes (needs repo + workflow) and repo name.";
  }).catch(function(e){
    console.error("GMR: arm alerts failed", e);
    status.textContent = "Push failed -- see console for details.";
  });
}

function sendTestAlert(){
  if (!requireGithubConnection()) return;
  var btn = $("#test-alert-btn");
  btn.disabled = true; btn.textContent = "Sending...";
  ghDispatchWorkflow("nri-email.yml", { test: "true" }).then(function(res){
    btn.disabled = false;
    btn.textContent = "Send me a test alert NOW";
    alert(res.ok ? "Test alert dispatched. Check your inbox within about a minute." : "Dispatch failed (status " + res.status + "). Check that the workflow file is pushed (Methodology tab) and your token has the workflow scope.");
  }).catch(function(e){
    btn.disabled = false; btn.textContent = "Send me a test alert NOW";
    console.error("GMR: test dispatch failed", e);
    alert("Dispatch failed -- see console for details.");
  });
}

function diagnoseSetup(){
  if (!requireGithubConnection()) return;
  var root = $("#diagnose-output");
  root.innerHTML = "<p class='muted small'>Running diagnostics...</p>";
  var repo = ghRepoPath();
  var checks = [
    {label:"Workflow file present", path:"/repos/" + repo + "/contents/.github/workflows/nri-email.yml"},
    {label:"Send script present", path:"/repos/" + repo + "/contents/scripts/maybe_send_email.py"},
    {label:"alerts.json present", path:"/repos/" + repo + "/contents/data/alerts.json"},
    {label:"watchlists.json present", path:"/repos/" + repo + "/contents/data/watchlists.json"},
    {label:"GMAIL_APP_PASSWORD secret set", path:"/repos/" + repo + "/actions/secrets/GMAIL_APP_PASSWORD"},
    {label:"Last workflow run status", path:"/repos/" + repo + "/actions/workflows/nri-email.yml/runs?per_page=1"}
  ];
  Promise.all(checks.map(function(c){ return ghGet(c.path).then(function(r){ return {label:c.label, ok:r.ok, json:r.json}; }); }))
    .then(function(results){
      var rows = results.map(function(r){
        var detail = "";
        if (r.label === "Last workflow run status"){
          var run = r.json && r.json.workflow_runs && r.json.workflow_runs[0];
          detail = run ? (run.status + "/" + (run.conclusion||"pending")) : "no runs yet";
          r.ok = !!run;
        }
        return "<tr><td>" + esc(r.label) + "</td><td class='" + (r.ok?"diag-ok":"diag-bad") + "'>" + (r.ok?"OK":"MISSING") + (detail?" (" + esc(detail) + ")":"") + "</td></tr>";
      });
      var emailOk = !!(STATE.alerts.channels && STATE.alerts.channels.email);
      rows.push("<tr><td>Email address configured</td><td class='" + (emailOk?"diag-ok":"diag-bad") + "'>" + (emailOk?"OK":"MISSING") + "</td></tr>");
      var sms = STATE.alerts.channels && STATE.alerts.channels.sms;
      var smsOk = !!(sms && sms.number && sms.carrier);
      rows.push("<tr><td>SMS gateway resolved</td><td class='" + (smsOk?"diag-ok":"diag-bad") + "'>" + (smsOk?"OK":"not configured (optional)") + "</td></tr>");
      root.innerHTML = "<table class='status-table'><tbody>" + rows.join("") + "</tbody></table>";
    })
    .catch(function(e){
      console.error("GMR: diagnose failed", e);
      root.innerHTML = "<p class='muted small'>Diagnostics failed -- check your token/repo and console.</p>";
    });
}
"""

JS_METHODOLOGY = r"""
// ---- Methodology tab ----------------------------------------------------
var METH_MODE = "featured";
var CADENCE_OPTIONS = ["daily","weekly","monthly","quarterly","yearly","off"];

RENDERERS.methodology = function(root){
  var wlKeys = Object.keys(STATE.watchlists.lists);
  root.innerHTML =
    "<div class='card'>" +
      "<h2>Methodology</h2>" +
      "<label>Show methodology for</label>" +
      "<select id='meth-select'>" +
        "<option value='featured'" + (METH_MODE==="featured"?" selected":"") + ">Featured index</option>" +
        wlKeys.map(function(k){ return "<option value='wl:" + esc(k) + "'" + (METH_MODE==="wl:"+k?" selected":"") + ">Watchlist: " + esc(STATE.watchlists.lists[k].label||k) + "</option>"; }).join("") +
      "</select>" +
    "</div>" +
    "<div id='meth-body'></div>";

  $("#meth-select").addEventListener("change", function(e){ METH_MODE = e.target.value; renderMethodologyBody(); });
  renderMethodologyBody();
};

function renderMethodologyBody(){
  var root = $("#meth-body");
  if (METH_MODE === "featured"){ renderFeaturedMethodology(root); return; }
  var key = METH_MODE.replace("wl:", "");
  var list = STATE.watchlists.lists[key];
  if (!list){ root.innerHTML = "<div class='card'><p class='muted small'>List not found.</p></div>"; return; }
  root.innerHTML =
    "<div class='card'>" +
      "<h3>" + esc(list.label||key) + "</h3>" +
      "<p class='muted small'>This is a hand-built list, no formal methodology. It is a flat collection of tickers -- add or remove them from the Watchlists tab.</p>" +
      "<div class='row'>" + list.tickers.map(function(t){ return "<span class='chip'>" + esc(t) + "</span>"; }).join("") + "</div>" +
    "</div>";
}

function renderFeaturedMethodology(root){
  var cons = STATE.constituents;
  var totalWeight = cons.reduce(function(a,c){ return a+c.weight; }, 0);
  var tier1 = cons.filter(function(c){ return c.tier===1; });
  var tier2 = cons.filter(function(c){ return c.tier!==1; });

  function tierTable(list, tierLabel){
    return "<div class='section-title'>" + tierLabel + "</div><table><thead><tr><th>Ticker</th><th>Name</th><th>Sector</th><th>Weight %</th><th></th></tr></thead><tbody>" +
      list.map(function(c){
        return "<tr><td>" + esc(c.ticker) + "</td><td>" + esc(c.name) + "</td><td class='muted'>" + esc(c.sector) + "</td>" +
          "<td><input data-weight='" + esc(c.ticker) + "' type='number' step='0.1' value='" + c.weight + "' style='width:80px'></td>" +
          "<td><button class='btn small ghost' data-remove-con='" + esc(c.ticker) + "'>Remove</button></td></tr>";
      }).join("") + "</tbody></table>";
  }

  root.innerHTML =
    "<div class='card'>" +
      "<h3>Tiered Weights</h3>" +
      "<p class='muted small'>Total allocated weight: " + fmtNum(totalWeight,1) + "% (should sum to 100%). Tier 1 names are core holdings; Tier 2 are satellite/emerging exposure.</p>" +
      tierTable(tier1, "Tier 1 -- Core") +
      tierTable(tier2, "Tier 2 -- Satellite") +
      "<div class='section-title'>Add Constituent</div>" +
      "<div class='grid cols-4'>" +
        "<div><label>Ticker</label><input id='con-ticker' type='text' style='text-transform:uppercase'></div>" +
        "<div><label>Name</label><input id='con-name' type='text'></div>" +
        "<div><label>Sector</label><input id='con-sector' type='text'></div>" +
        "<div><label>Weight %</label><input id='con-weight' type='number' value='5'></div>" +
      "</div>" +
      "<div class='cta-row'><button class='btn secondary' id='con-add-btn'>Add constituent</button><button class='btn' id='con-save-btn'>Save weights</button><span id='con-saved' class='footer-note'></span></div>" +
    "</div>" +
    "<div class='card' id='meth-email-card'></div>";

  $all("[data-remove-con]", root).forEach(function(b){
    b.addEventListener("click", function(){
      STATE.constituents = STATE.constituents.filter(function(c){ return c.ticker !== b.dataset.removeCon; });
      saveConstituents();
      renderFeaturedMethodology(root);
    });
  });
  $("#con-add-btn").addEventListener("click", function(){
    var ticker = ($("#con-ticker").value||"").trim().toUpperCase();
    if (!ticker) return;
    STATE.constituents.push({
      ticker:ticker, name: $("#con-name").value.trim()||ticker, sector: $("#con-sector").value.trim()||"Uncategorized",
      tier:2, weight: parseFloat($("#con-weight").value)||1
    });
    saveConstituents();
    renderFeaturedMethodology(root);
  });
  $("#con-save-btn").addEventListener("click", function(){
    $all("[data-weight]", root).forEach(function(inp){
      var c = STATE.constituents.filter(function(x){ return x.ticker===inp.dataset.weight; })[0];
      if (c) c.weight = parseFloat(inp.value)||0;
    });
    saveConstituents();
    $("#con-saved").textContent = "Saved.";
  });

  renderEmailDigestCard();
}

function renderEmailDigestCard(){
  var root = $("#meth-email-card");
  var es = STATE.emailSettings;
  root.innerHTML =
    "<h3>Email Digest Schedule</h3>" +
    "<div class='row'>" +
      CADENCE_OPTIONS.map(function(c){
        return "<label class='chip" + (es.cadence===c?" active":"") + "' data-cadence='" + c + "' style='cursor:pointer'>" + c + "</label>";
      }).join("") +
    "</div>" +
    "<div class='grid cols-2' style='margin-top:12px'>" +
      "<div><label>Gmail address (used as sender + digest recipient)</label><input id='meth-email' type='email' value='" + esc(es.email||"") + "'></div>" +
      "<div><label>owner/repo</label><input id='meth-repo' type='text' placeholder='yourname/GMR' value='" + esc(STATE.githubRepo||"") + "'></div>" +
    "</div>" +
    "<div class='grid cols-2'>" +
      "<div><label>GitHub Personal Access Token (repo + workflow scopes)</label><input id='meth-token' type='text' placeholder='ghp_...' value='" + esc(STATE.githubToken||"") + "'></div>" +
    "</div>" +
    "<div class='cta-row'><button class='btn' id='meth-turn-on'>Turn on scheduled emails</button><span id='meth-status' class='footer-note'></span></div>";

  $all("[data-cadence]", root).forEach(function(chip){
    chip.addEventListener("click", function(){
      STATE.emailSettings.cadence = chip.dataset.cadence;
      saveEmailSettings();
      renderEmailDigestCard();
    });
  });

  $("#meth-turn-on").addEventListener("click", function(){
    STATE.emailSettings.email = $("#meth-email").value.trim();
    STATE.emailSettings.to = STATE.emailSettings.email;
    saveEmailSettings();
    STATE.githubRepo = $("#meth-repo").value.trim();
    STATE.githubToken = $("#meth-token").value.trim();
    lsSet("githubRepo", STATE.githubRepo);
    lsSet("githubToken", STATE.githubToken);

    if (!STATE.githubRepo || !STATE.githubToken){
      $("#meth-status").textContent = "Enter owner/repo and a token first.";
      return;
    }
    var status = $("#meth-status");
    status.textContent = "Pushing workflow + scripts to your repo...";
    var files = STATE.deployFiles || {};
    Promise.all([
      ghPutFile(".github/workflows/nri-email.yml", files.workflow || "", "GMR: enable scheduled emails"),
      ghPutFile("scripts/maybe_send_email.py", files.sendScript || "", "GMR: enable scheduled emails"),
      ghPutFile("scripts/indicators.py", files.indicators || "", "GMR: enable scheduled emails"),
      ghPutFile("data/email_settings.json", STATE.emailSettings, "GMR: update email settings")
    ]).then(function(results){
      var allOk = results.every(function(r){ return r.ok; });
      status.textContent = allOk
        ? "Scheduled emails are on. Add the GMAIL_APP_PASSWORD secret in your repo settings, then use Alerts → Send a test alert."
        : "Something failed -- check the token has repo + workflow scopes and the repo name is correct.";
    }).catch(function(e){
      console.error("GMR: turn on scheduled emails failed", e);
      status.textContent = "Push failed -- see console for details.";
    });
  });
}
"""

APP_JS = JS_OPEN + JS_CORE + JS_PROXY + JS_ROUTER + JS_DASHBOARD + JS_WATCHLISTS + JS_COMPANIES + JS_OPTIMIZER + JS_BACKTEST + JS_UPDATES + JS_PREIPO + JS_PROFILE + JS_GITHUB + JS_ALERTS + JS_METHODOLOGY + JS_CLOSE


if __name__ == "__main__":
    build()
