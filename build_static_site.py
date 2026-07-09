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
        "relationships": load_json("relationships.json"),
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
.chart-toolbar{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:10px}
.seg{display:inline-flex;border:1px solid var(--border);border-radius:8px;overflow:hidden;background:var(--bg2)}
.seg button{background:none;border:none;color:var(--muted);padding:6px 11px;font-size:12.5px;font-weight:600;cursor:pointer;border-right:1px solid var(--border)}
.seg button:last-child{border-right:none}
.seg button:hover{color:var(--text)}
.seg button.on{background:var(--accent);color:#04211d}
.adv-readout{display:flex;gap:14px;flex-wrap:wrap;align-items:center;font-size:12.5px;color:var(--muted);
  padding:6px 2px;margin-bottom:2px;min-height:26px}
.adv-readout b{color:var(--text);font-weight:700}
.adv-readout .ro-date{color:var(--text);font-weight:700;font-size:13px}
.zoom-hint{margin-left:auto;font-size:11.5px;opacity:.75}
@media(max-width:720px){ .zoom-hint{display:none} }
td.caret{color:var(--muted);width:22px;text-align:center;user-select:none}
tr.row-open{background:var(--panel2)}
tr.row-open td.caret{color:var(--accent)}
.topsearch-wrap{position:relative}
.topsearch{display:flex;align-items:center;gap:0;background:var(--bg2);border:1px solid var(--border);border-radius:8px;overflow:hidden}
.topsearch input{border:none;background:none;width:210px;padding:7px 10px;font-size:13px;color:var(--text)}
.topsearch input:focus{outline:none}
.topsearch button{border:none;background:var(--panel2);color:var(--text);padding:7px 11px;cursor:pointer;font-size:13px}
.topsearch button:hover{background:var(--accent);color:#04211d}
@media(max-width:900px){ .topsearch-wrap{order:3} .topsearch input{width:150px} }
.search-results{position:absolute;top:calc(100% + 4px);right:0;width:340px;max-width:80vw;background:var(--panel);
  border:1px solid var(--border);border-radius:10px;box-shadow:0 12px 40px rgba(0,0,0,.5);z-index:100;
  max-height:60vh;overflow-y:auto;display:none}
.search-results.open{display:block}
.sr-item{display:flex;align-items:center;gap:10px;padding:9px 12px;border-bottom:1px solid var(--border);cursor:pointer}
.sr-item:last-child{border-bottom:none}
.sr-item:hover,.sr-item.active{background:var(--panel2)}
.sr-main{flex:1;min-width:0}
.sr-sym{font-weight:700;font-size:13.5px}
.sr-name{font-size:11.5px;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.sr-exch{font-size:10.5px;color:var(--muted);border:1px solid var(--border);border-radius:5px;padding:1px 5px}
.sr-add{border:1px solid var(--border);background:var(--bg2);color:var(--accent);border-radius:6px;
  padding:4px 8px;font-size:12px;cursor:pointer;white-space:nowrap;font-weight:700}
.sr-add:hover{background:var(--accent);color:#04211d;border-color:var(--accent)}
.sr-add.added{color:var(--up);border-color:var(--up)}
.sr-msg{padding:10px 12px;color:var(--muted);font-size:12.5px}
.wl-menu{position:absolute;z-index:200;min-width:220px;max-width:280px;background:var(--panel);
  border:1px solid var(--border);border-radius:10px;box-shadow:0 12px 40px rgba(0,0,0,.55);overflow:hidden;padding:4px}
.wl-menu .wm-head{padding:7px 10px 5px;font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}
.wm-item{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:8px 10px;border-radius:7px;
  cursor:pointer;font-size:13px}
.wm-item:hover{background:var(--panel2)}
.wm-item .wm-meta{font-size:11px;color:var(--muted)}
.wm-item.has{color:var(--muted)}
.wm-item.has .wm-meta{color:var(--up)}
.wm-item.wm-new{color:var(--accent);font-weight:700;border-top:1px solid var(--border);margin-top:2px}
.wl-toast{position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:var(--panel2);
  border:1px solid var(--accent);color:var(--text);padding:10px 16px;border-radius:8px;font-size:13px;
  z-index:300;box-shadow:0 8px 30px rgba(0,0,0,.5);opacity:0;transition:opacity .2s}
.wl-toast.show{opacity:1}
.heat-sector{margin-bottom:16px}
.heat-sector-head{font-size:12px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);margin:0 0 6px;font-weight:700}
.heat-tiles{display:grid;grid-template-columns:repeat(auto-fill,minmax(84px,1fr));grid-auto-rows:64px;gap:5px}
.heat-tile{border-radius:7px;padding:7px 8px;display:flex;flex-direction:column;justify-content:center;
  cursor:pointer;border:1px solid rgba(255,255,255,.06);overflow:hidden;transition:transform .08s}
.heat-tile:hover{transform:scale(1.04);border-color:rgba(255,255,255,.25);z-index:2}
.heat-tile .ht-sym{font-weight:800;font-size:14px;color:#fff}
.heat-tile .ht-chg{font-size:12px;color:rgba(255,255,255,.9);font-weight:600}
.heat-tile.md{grid-column:span 1;grid-row:span 1}
.heat-tile.lg{grid-column:span 2;grid-row:span 1}
.heat-tile.xl{grid-column:span 2;grid-row:span 2}
.heat-tile.xl .ht-sym{font-size:18px}
.heat-tile.sm .ht-sym{font-size:12.5px}
@media(max-width:560px){ .heat-tile.xl,.heat-tile.lg{grid-column:span 2} }
.chip.mgmt{gap:8px;padding-right:6px}
.chip.mgmt > span:first-child{cursor:pointer}
.chip-x{cursor:pointer;opacity:.6;padding:0 3px;font-weight:800;border-radius:4px}
.chip-x:hover{opacity:1;background:rgba(255,255,255,.12)}
.archived-block{margin-top:8px;width:100%}
.archived-block summary{cursor:pointer;color:var(--muted);font-size:12.5px;padding:4px 0}
.archived-block summary:hover{color:var(--text)}
.kg-crumb{font-size:13px;color:var(--muted);margin-bottom:4px}
.kg-crumb .link{color:var(--accent);cursor:pointer}
.kg-crumb .link:hover{text-decoration:underline}
.kg-sources{margin-top:8px}
.kg-sources summary{cursor:pointer;color:var(--accent);font-size:12.5px;font-weight:600}
.kg-sources summary:hover{text-decoration:underline}
.kg-sources code{background:var(--bg2);padding:1px 5px;border-radius:4px;font-size:11.5px}
.stats-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:0 26px}
@media(max-width:900px){ .stats-grid{grid-template-columns:repeat(2,1fr)} }
@media(max-width:560px){ .stats-grid{grid-template-columns:1fr} }
.stat-row{display:flex;justify-content:space-between;gap:12px;padding:9px 2px;border-bottom:1px solid var(--border);font-size:13.5px}
.stat-row .lbl{color:var(--muted)}
.stat-row .val{font-weight:700;text-align:right}
.overview{display:grid;grid-template-columns:1.7fr 1fr;gap:20px}
@media(max-width:760px){ .overview{grid-template-columns:1fr} }
.overview .prof{display:grid;grid-template-columns:1fr 1fr;gap:14px;align-content:start}
.overview .prof .big{font-size:20px;font-weight:800}
.overview .prof .sub{font-size:12px;color:var(--muted)}
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
    <div class="topsearch-wrap" id="topsearch-wrap">
      <form class="topsearch" id="topsearch" autocomplete="off">
        <input id="topsearch-input" type="text" placeholder="Search ticker or company" aria-label="Search ticker or company">
        <button type="submit" aria-label="Search">&#128269;</button>
      </form>
      <div class="search-results" id="search-results"></div>
    </div>
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
function fmtBig(v){
  if (v == null || isNaN(v)) return "--";
  var a = Math.abs(v);
  if (a >= 1e12) return (v/1e12).toFixed(2) + "T";
  if (a >= 1e9) return (v/1e9).toFixed(2) + "B";
  if (a >= 1e6) return (v/1e6).toFixed(2) + "M";
  if (a >= 1e3) return (v/1e3).toFixed(2) + "K";
  return String(Math.round(v));
}
function fmtInt(v){ return (v == null || isNaN(v)) ? "--" : Math.round(v).toLocaleString(); }
function fmtDateTs(ts){
  if (!ts) return "--";
  var d = new Date(ts * 1000);
  if (isNaN(d.getTime())) return "--";
  return d.toLocaleDateString("en-US", {year:"numeric", month:"short", day:"numeric"});
}
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
// Session storage -- for sensitive values (the GitHub token). Cleared when the
// browser tab closes, so it is not left behind on a shared computer.
function ssGet(key, fallback){
  try{ var raw = sessionStorage.getItem(LS_PREFIX + key); return raw == null ? fallback : JSON.parse(raw); }catch(e){ return fallback; }
}
function ssSet(key, val){
  try{ sessionStorage.setItem(LS_PREFIX + key, JSON.stringify(val)); }catch(e){}
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
  githubToken: ssGet("githubToken", ""),
  githubRepo: lsGet("githubRepo", ""),
  deployFiles: window.GMR_DEPLOY_FILES || {},
  relationships: SEED.relationships || {types:{}, edges:[]}
};
function saveWatchlists(){ lsSet("watchlists", STATE.watchlists); }
function saveProfile(){ lsSet("profile", STATE.profile); }
function saveAlerts(){ lsSet("alerts", STATE.alerts); }
function saveEmailSettings(){ lsSet("emailSettings", STATE.emailSettings); }

// ---- indexes: named weighted baskets you can track like the nuclear one ---
// STATE.constituents always points at the ACTIVE index's constituent array, so
// every existing consumer (dashboard chart/KPIs, methodology, backtest) follows
// whichever index is selected without further changes.
STATE.indexes = lsGet("indexes", null);
if (!STATE.indexes){
  STATE.indexes = { nuclear: { label:"Nuclear", benchmarks:["URA","NLR"], constituents: STATE.constituents } };
}
STATE.activeIndex = lsGet("activeIndex", "nuclear");
if (!STATE.indexes[STATE.activeIndex]) STATE.activeIndex = Object.keys(STATE.indexes)[0] || "nuclear";
STATE.constituents = (STATE.indexes[STATE.activeIndex] || {}).constituents || STATE.constituents;

function saveIndexes(){ lsSet("indexes", STATE.indexes); lsSet("activeIndex", STATE.activeIndex); }
function activeIndexKeys(){ return Object.keys(STATE.indexes).filter(function(k){ return !STATE.indexes[k].archived; }); }
function archiveIndex(key){
  if (key === "nuclear"){ alert("The featured Nuclear index cannot be archived."); return; }
  STATE.indexes[key].archived = true;
  if (STATE.activeIndex === key) setActiveIndex(activeIndexKeys()[0] || "nuclear");
  else saveIndexes();
}
function saveConstituents(){ // active index edited in place -> persist indexes
  if (STATE.indexes[STATE.activeIndex]) STATE.indexes[STATE.activeIndex].constituents = STATE.constituents;
  saveIndexes();
}
function getActiveIndex(){ return STATE.indexes[STATE.activeIndex] || {label:"Index", benchmarks:[], constituents:STATE.constituents}; }
function setActiveIndex(key){
  if (!STATE.indexes[key]) return;
  STATE.activeIndex = key;
  STATE.constituents = STATE.indexes[key].constituents;
  saveIndexes();
}
function createIndexFromWeights(name, tickers, weightMap){
  var key = "idx-" + (name.toLowerCase().replace(/[^a-z0-9]+/g,"-").replace(/(^-|-$)/g,"") || uid());
  var cons = tickers.map(function(t){
    return { ticker:t, name:t, sector:"Uncategorized", tier: (weightMap[t]>=8?1:2), weight: weightMap[t]!=null?weightMap[t]:(100/tickers.length) };
  });
  STATE.indexes[key] = { label:name, benchmarks:["SPY","QQQ"], constituents:cons };
  saveIndexes();
  return key;
}
function createIndexFromTickers(name, tickers, method, capByTicker){
  var weightMap = {};
  if (method === "market-cap" && capByTicker){
    var total = tickers.reduce(function(a,t){ return a + (capByTicker[t]||0); }, 0);
    tickers.forEach(function(t){ weightMap[t] = total>0 ? Math.round((capByTicker[t]||0)/total*1000)/10 : 100/tickers.length; });
  } else {
    var w = Math.round(1000/tickers.length)/10;
    tickers.forEach(function(t){ weightMap[t] = w; });
  }
  return createIndexFromWeights(name, tickers, weightMap);
}
function deleteIndex(key){
  if (key === "nuclear"){ alert("The featured Nuclear index cannot be deleted."); return; }
  delete STATE.indexes[key];
  if (STATE.activeIndex === key) setActiveIndex(Object.keys(STATE.indexes)[0]);
  else saveIndexes();
}

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
// IMPORTANT: these are ranked by what works IN A BROWSER from a GitHub Pages
// origin -- which is the opposite of what curl/server tests show. corsproxy.io
// 403s to curl (no Origin) but works great from a real browser and is the most
// reliable here, so it leads. allorigins is slow/flaky browser-side. Bump
// PROXY_VERSION whenever this list changes to wipe stale per-user health data
// that might otherwise wrongly deprioritize a now-working proxy.
var PROXY_VERSION = 3;
var PROXIES = [
  {name:"corsproxy",      build:function(u){ return "https://corsproxy.io/?url=" + encodeURIComponent(u); }},
  {name:"allorigins-get", build:function(u){ return "https://api.allorigins.win/get?url=" + encodeURIComponent(u); }, wrapped:true},
  {name:"allorigins-raw", build:function(u){ return "https://api.allorigins.win/raw?url=" + encodeURIComponent(u); }},
  {name:"codetabs",       build:function(u){ return "https://api.codetabs.com/v1/proxy?quest=" + encodeURIComponent(u); }},
  {name:"corslol",        build:function(u){ return "https://api.cors.lol/?url=" + encodeURIComponent(u); }}
];
(function resetProxyHealthIfStale(){
  if (lsGet("proxyVersion", 0) !== PROXY_VERSION){
    lsSet("proxyHealth", {}); lsSet("lastGoodProxy", null); lsSet("proxyVersion", PROXY_VERSION);
  }
})();
function proxyHealth(){ return lsGet("proxyHealth", {}); }
function saveProxyHealth(h){ lsSet("proxyHealth", h); }
function orderedProxies(){
  var health = proxyHealth();
  var lastGood = lsGet("lastGoodProxy", null);
  var list = PROXIES.slice();
  // sort by fewest fails, preferring the last-known-good route -- but never
  // permanently exclude anyone (a proxy that works resets its count on success).
  list.sort(function(a,b){
    if (a.name === lastGood) return -1;
    if (b.name === lastGood) return 1;
    var fa = (health[a.name]||{}).fails||0, fb = (health[b.name]||{}).fails||0;
    return fa - fb;
  });
  return list;
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
  var q = res.indicators.quote[0];
  var opens = q.open || [], highs = q.high || [], lows = q.low || [];
  var closes = q.close || [], volumes = q.volume || [];
  var dates = ts.map(function(t){ return new Date(t*1000).toISOString().slice(0,10); });
  var out = {dates:[], opens:[], highs:[], lows:[], closes:[], volumes:[]};
  for (var i=0;i<dates.length;i++){
    if (closes[i]!=null){
      var c = closes[i];
      out.dates.push(dates[i]);
      out.opens.push(opens[i]!=null?opens[i]:c);
      out.highs.push(highs[i]!=null?highs[i]:Math.max(opens[i]!=null?opens[i]:c, c));
      out.lows.push(lows[i]!=null?lows[i]:Math.min(opens[i]!=null?opens[i]:c, c));
      out.closes.push(c);
      out.volumes.push(volumes[i]||0);
    }
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
  var dates=[], opens=[], highs=[], lows=[], closes=[], volumes=[];
  var d = new Date(); d.setDate(d.getDate()-days);
  for (i=0;i<days;i++){
    var day = d.getDay();
    if (day!==0 && day!==6){
      // gaussian-ish shock via sum of uniforms; occasional vol spike
      var shock = (rnd()+rnd()+rnd()-1.5) * vol;
      if (rnd() > 0.97) shock *= 3;
      var open = price;
      price = Math.max(1, price*(1 + drift + shock));
      var hi = Math.max(open, price) * (1 + rnd()*vol*0.5);
      var lo = Math.min(open, price) * (1 - rnd()*vol*0.5);
      dates.push(new Date(d).toISOString().slice(0,10));
      opens.push(Math.round(open*100)/100);
      highs.push(Math.round(hi*100)/100);
      lows.push(Math.round(lo*100)/100);
      closes.push(Math.round(price*100)/100);
      var baseVol = 400000 + (seed % 9)*300000;
      volumes.push(Math.round(baseVol * (0.6 + rnd()*1.6)));
    }
    d.setDate(d.getDate()+1);
  }
  return {dates:dates, opens:opens, highs:highs, lows:lows, closes:closes, volumes:volumes, synthetic:true};
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
        return {dates:j.dates, opens:j.opens, highs:j.highs, lows:j.lows, closes:j.closes, volumes:j.volumes, updated:j.updated, fundamentals:j.fundamentals||null};
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
  {key:"heatmap",     label:"Heatmap"},
  {key:"moneyflow",   label:"Money Flow"},
  {key:"watchlists",  label:"Watchlists"},
  {key:"indexes",     label:"Indexes"},
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

// Local universe (ticker + name) from constituents + presets, for instant
// results and as a fallback when the live search API is unreachable.
function localSearchIndex(){
  var seen = {}, out = [];
  (STATE.constituents||[]).forEach(function(c){ if(!seen[c.ticker]){ seen[c.ticker]=1; out.push({symbol:c.ticker, name:c.name, exch:""}); } });
  (STATE.presets||[]).forEach(function(p){ (p.tickers||[]).forEach(function(t){ if(!seen[t]){ seen[t]=1; out.push({symbol:t, name:"", exch:""}); } }); });
  return out;
}
function localSearch(q){
  q = q.toLowerCase();
  return localSearchIndex().filter(function(r){
    return r.symbol.toLowerCase().indexOf(q) !== -1 || (r.name && r.name.toLowerCase().indexOf(q) !== -1);
  }).slice(0, 8);
}
// Live search via Yahoo's public search endpoint (no auth), through the CORS
// proxy chain. Resolves ticker OR company name to matching symbols.
var US_EXCH = {"NASDAQ":1,"NYSE":1,"NYSEArca":1,"NYSE American":1,"NYSE Arca":1,"NYSEAmerican":1,"NCM":1,"NMS":1,"NGM":1,"PCX":1,"BATS":1,"Cboe US":1,"OTC Markets":1,"OTC":1};
function liveSearch(q){
  var url = "https://query2.finance.yahoo.com/v1/finance/search?q=" + encodeURIComponent(q) + "&quotesCount=12&newsCount=0";
  return fetchViaProxies(url, 6000).then(function(txt){
    var quotes = (JSON.parse(txt).quotes) || [];
    var items = quotes.filter(function(x){
      return x.symbol && (x.quoteType === "EQUITY" || x.quoteType === "ETF");
    }).map(function(x){
      var usListed = US_EXCH[x.exchDisp] || x.symbol.indexOf(".") === -1;
      return { symbol: x.symbol, name: x.shortname || x.longname || "", exch: x.exchDisp || "", us: usListed ? 1 : 0 };
    });
    // US primary listings first (Yahoo returns lots of foreign cross-listings)
    items.sort(function(a,b){ return b.us - a.us; });
    return items.slice(0, 8);
  });
}

function wireTopSearch(){
  var form = document.getElementById("topsearch");
  var input = document.getElementById("topsearch-input");
  var box = document.getElementById("search-results");
  var wrap = document.getElementById("topsearch-wrap");
  if (!form || !input || !box) return;
  var timer = null, seq = 0, activeIdx = -1, results = [];

  function close(){ box.className = "search-results"; box.innerHTML = ""; activeIdx = -1; }
  function openCompany(sym){
    CO_TICKER = sym.toUpperCase(); lsSet("companiesTicker", CO_TICKER);
    input.value = ""; close(); input.blur();
    showTab("companies");
  }
  function addToWatchlist(sym, btn){
    openWatchlistMenu(btn, sym, function(){ btn.textContent = "Added"; btn.className = "sr-add added"; });
  }
  function render(items, note){
    results = items || [];
    if (note){ box.innerHTML = "<div class='sr-msg'>" + esc(note) + "</div>"; box.className = "search-results open"; return; }
    if (!results.length){ box.innerHTML = "<div class='sr-msg'>No matches.</div>"; box.className = "search-results open"; return; }
    box.innerHTML = results.map(function(r, i){
      return "<div class='sr-item" + (i===activeIdx?" active":"") + "' data-i='" + i + "'>" +
        "<div class='sr-main' data-open='" + esc(r.symbol) + "'>" +
          "<div class='sr-sym'>" + esc(r.symbol) + (r.exch?" <span class='sr-exch'>" + esc(r.exch) + "</span>":"") + "</div>" +
          (r.name ? "<div class='sr-name'>" + esc(r.name) + "</div>" : "") +
        "</div>" +
        "<button class='sr-add' data-add='" + esc(r.symbol) + "'>+ Watchlist</button>" +
      "</div>";
    }).join("");
    box.className = "search-results open";
    $all("[data-open]", box).forEach(function(el){ el.addEventListener("click", function(){ openCompany(el.dataset.open); }); });
    $all("[data-add]", box).forEach(function(b){ b.addEventListener("click", function(e){ e.stopPropagation(); addToWatchlist(b.dataset.add, b); }); });
  }
  function doSearch(q){
    var mySeq = ++seq;
    // instant local results first
    var loc = localSearch(q);
    render(loc.length ? loc : null, loc.length ? null : "Searching...");
    liveSearch(q).then(function(items){
      if (mySeq !== seq) return; // a newer query superseded this one
      // merge: live results first, then any local-only symbols
      var syms = {}; var merged = [];
      items.forEach(function(r){ if(!syms[r.symbol]){ syms[r.symbol]=1; merged.push(r); } });
      loc.forEach(function(r){ if(!syms[r.symbol]){ syms[r.symbol]=1; merged.push(r); } });
      render(merged.slice(0, 10));
    }).catch(function(){
      if (mySeq !== seq) return;
      render(loc, loc.length ? null : "Search unavailable -- type an exact ticker and press Enter.");
    });
  }

  input.addEventListener("input", function(){
    var q = input.value.trim();
    activeIdx = -1;
    if (timer) clearTimeout(timer);
    if (q.length < 1){ close(); return; }
    timer = setTimeout(function(){ doSearch(q); }, 220);
  });
  input.addEventListener("keydown", function(e){
    if (!results.length) return;
    if (e.key === "ArrowDown"){ e.preventDefault(); activeIdx = Math.min(results.length-1, activeIdx+1); render(results); }
    else if (e.key === "ArrowUp"){ e.preventDefault(); activeIdx = Math.max(0, activeIdx-1); render(results); }
    else if (e.key === "Escape"){ close(); }
  });
  form.addEventListener("submit", function(e){
    e.preventDefault();
    if (activeIdx >= 0 && results[activeIdx]){ openCompany(results[activeIdx].symbol); return; }
    if (results.length){ openCompany(results[0].symbol); return; }
    var raw = (input.value||"").trim();
    if (raw) openCompany(raw.split(/[\s-]/)[0]);
  });
  document.addEventListener("click", function(e){
    if (wrap && !wrap.contains(e.target) && !(e.target.closest && e.target.closest(".wl-menu"))) close();
  });
}

function init(){
  renderNav();
  wireTopSearch();
  updateMarketStatus();
  setInterval(updateMarketStatus, 60000);
  // load the SEC-filer index so Money Flow can offer the whole-market scope
  fetch("data/sec/_index.json", {cache:"default"}).then(function(r){ return r.ok?r.json():null; }).then(function(j){ if(j) window.GMR_SEC_INDEX = j; }).catch(function(){});
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
      "<div class='card'><div class='flex-between'><h3 style='margin:0'>Featured Index</h3>" +
        "<select id='dash-index-select' style='width:auto'>" + activeIndexKeys().map(function(k){ return "<option value='" + esc(k) + "'" + (k===STATE.activeIndex?" selected":"") + ">" + esc(STATE.indexes[k].label||k) + "</option>"; }).join("") + "</select></div>" +
        "<div class='chart-wrap' style='margin-top:10px'><canvas id='dash-index-chart'></canvas></div></div>" +
      "<div class='card'><h3>Sector Weights</h3><div class='chart-wrap'><canvas id='dash-sector-donut'></canvas></div></div>" +
    "</div>" +
    "<div class='grid cols-2'>" +
      "<div class='card'><h3>Leaders (Today)</h3><div id='dash-leaders'><p class='muted small'>Loading...</p></div></div>" +
      "<div class='card'><h3>Laggards (Today)</h3><div id='dash-laggards'><p class='muted small'>Loading...</p></div></div>" +
    "</div>" +
    "<div class='card'>" +
      "<h3>Your Watchlists</h3>" +
      "<div id='dash-watchlist-summary'></div>" +
    "</div>";

  $("#cta-watchlists").addEventListener("click", function(){ showTab("watchlists"); });
  $("#cta-alerts").addEventListener("click", function(){ showTab("alerts"); });
  $("#cta-optimizer").addEventListener("click", function(){ showTab("optimizer"); });
  $("#dash-index-select").addEventListener("change", function(e){ setActiveIndex(e.target.value); showTab("dashboard"); });

  renderWatchlistSummary($("#dash-watchlist-summary"));
  renderSectorDonut($("#dash-sector-donut"));
  renderIndexChart($("#dash-index-chart"));
  renderDashboardKPIs();
};

function moversTable(root, rows){
  if (!rows.length){ root.innerHTML = "<p class='muted small'>No data.</p>"; return; }
  root.innerHTML = "<table><tbody>" + rows.map(function(r){
    return "<tr class='clickable' data-mover='" + esc(r.ticker) + "'><td><b>" + esc(r.ticker) + "</b></td>" +
      "<td>" + fmtPrice(r.price) + "</td>" +
      "<td class='" + pctClass(r.chg) + "' style='text-align:right'>" + fmtPct(r.chg) + "</td></tr>";
  }).join("") + "</tbody></table>";
  $all("[data-mover]", root).forEach(function(tr){
    tr.addEventListener("click", function(){ CO_TICKER = tr.dataset.mover; lsSet("companiesTicker", CO_TICKER); showTab("companies"); });
  });
}

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
      movers.push({ticker:r.con.ticker, chg:chg, price:closes[closes.length-1]});
    });
    var byChg = movers.slice().sort(function(a,b){ return b.chg-a.chg; });
    var topAbs = movers.slice().sort(function(a,b){ return Math.abs(b.chg)-Math.abs(a.chg); })[0];

    var elLevel = $("#kpi-level"); if (elLevel) elLevel.textContent = fmtNum(levelNow, 1);
    var elChg = $("#kpi-change");
    if (elChg){ elChg.textContent = fmtPct(dayChg); elChg.className = "kpi-val " + pctClass(dayChg); }
    var elBreadth = $("#kpi-breadth"); if (elBreadth) elBreadth.textContent = accum + " / " + rows.length;
    var elTop = $("#kpi-topmover");
    if (elTop && topAbs){ elTop.textContent = topAbs.ticker; elTop.className = "kpi-val " + pctClass(topAbs.chg); }
    var elTopSub = $("#kpi-topmover-sub"); if (elTopSub && topAbs) elTopSub.textContent = fmtPct(topAbs.chg) + " today";

    var leadersEl = $("#dash-leaders"); if (leadersEl) moversTable(leadersEl, byChg.slice(0,5));
    var laggardsEl = $("#dash-laggards"); if (laggardsEl) moversTable(laggardsEl, byChg.slice(-5).reverse());
  }).catch(function(e){ console.error("GMR: dashboard KPIs failed", e); });
}

function renderWatchlistSummary(root){
  var lists = STATE.watchlists.lists || {};
  var keys = activeWatchlistKeys();
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
      data: { labels: baseDates, datasets: [{ label:"GMR " + (getActiveIndex().label||"") + " Index", data: composite, borderColor:"#4fd1c5", backgroundColor:"rgba(79,209,197,.12)", fill:true, pointRadius:0, tension:.15 }] },
      options: { maintainAspectRatio:false, scales:{ x:{ ticks:{ color:"#93a2bb", maxTicksLimit:8 }, grid:{color:"#1b2536"} }, y:{ ticks:{color:"#93a2bb"}, grid:{color:"#1b2536"} } }, plugins:{ legend:{ labels:{ color:"#93a2bb" } } } }
    });
  }).catch(function(e){ console.error("GMR: index chart failed", e); canvas.parentElement.innerHTML = "<p class='muted'>Chart unavailable right now.</p>"; });
}
"""

JS_WATCHLISTS = r"""
// ---- Watchlists tab -------------------------------------------------------
var WL_EXPANDED = null;
var DEFAULT_INDICATORS = {sma:true, ema:false, rsi:true, bollinger:false, macd:true, vwap:false};

// ---- shared "add to watchlist" picker (used by Companies + search) --------
function toast(msg){
  var t = document.createElement("div");
  t.className = "wl-toast";
  t.innerHTML = msg;
  document.body.appendChild(t);
  requestAnimationFrame(function(){ t.className = "wl-toast show"; });
  setTimeout(function(){ t.className = "wl-toast"; setTimeout(function(){ if(t.parentNode) t.parentNode.removeChild(t); }, 250); }, 2200);
}
function closeWatchlistMenu(){
  var m = document.getElementById("wl-menu");
  if (m){ if (m._outside) document.removeEventListener("mousedown", m._outside); m.remove(); }
}
// anchor: element to position under; ticker: symbol; onAdd(key,list) callback.
function openWatchlistMenu(anchor, ticker, onAdd){
  ticker = String(ticker || "").toUpperCase();
  if (!ticker) return;
  closeWatchlistMenu();
  var lists = STATE.watchlists.lists || {};
  var keys = Object.keys(lists);
  var menu = document.createElement("div");
  menu.className = "wl-menu"; menu.id = "wl-menu";
  var rows = keys.map(function(k){
    var has = (lists[k].tickers || []).indexOf(ticker) !== -1;
    return "<div class='wm-item" + (has?" has":"") + "' data-wl='" + esc(k) + "'>" +
      "<span>" + esc(lists[k].label || k) + "</span>" +
      "<span class='wm-meta'>" + (has ? "&#10003; added" : (lists[k].tickers||[]).length + " names") + "</span></div>";
  }).join("");
  menu.innerHTML = "<div class='wm-head'>Add " + esc(ticker) + " to</div>" + rows +
    "<div class='wm-item wm-new' data-wl-new='1'>+ New watchlist</div>";
  document.body.appendChild(menu);

  // position under the anchor, clamped to the viewport
  var r = anchor.getBoundingClientRect();
  var mw = menu.offsetWidth || 240;
  var left = Math.min(r.left + window.scrollX, window.scrollX + document.documentElement.clientWidth - mw - 8);
  menu.style.top = (r.bottom + window.scrollY + 4) + "px";
  menu.style.left = Math.max(8, left) + "px";

  function pick(key){
    var list = STATE.watchlists.lists[key];
    if (list.tickers.indexOf(ticker) === -1) list.tickers.push(ticker);
    STATE.watchlists.active = key;
    saveWatchlists();
    closeWatchlistMenu();
    toast("Added <b>" + esc(ticker) + "</b> to <b>" + esc(list.label || key) + "</b>");
    if (onAdd) onAdd(key, list);
  }
  $all("[data-wl]", menu).forEach(function(el){ el.addEventListener("click", function(){ pick(el.dataset.wl); }); });
  var newEl = menu.querySelector("[data-wl-new]");
  newEl.addEventListener("click", function(){
    var name = prompt("Name for the new watchlist:");
    if (!name) return;
    name = name.trim(); if (!name) return;
    var key = name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "") || uid();
    if (!STATE.watchlists.lists[key]) STATE.watchlists.lists[key] = {label:name, desc:"", tickers:[], indicators: Object.assign({}, DEFAULT_INDICATORS)};
    pick(key);
  });
  // if there are no lists yet, jump straight to creating one
  if (!keys.length){ closeWatchlistMenu(); newEl = null; var nm = prompt("Name your first watchlist:"); if (nm){ var k = nm.toLowerCase().replace(/[^a-z0-9]+/g,"-").replace(/(^-|-$)/g,"")||uid(); STATE.watchlists.lists[k]={label:nm,desc:"",tickers:[ticker],indicators:Object.assign({},DEFAULT_INDICATORS)}; STATE.watchlists.active=k; saveWatchlists(); toast("Added <b>"+esc(ticker)+"</b> to <b>"+esc(nm)+"</b>"); if(onAdd) onAdd(k, STATE.watchlists.lists[k]); } return; }

  menu._outside = function(e){ if (!menu.contains(e.target) && e.target !== anchor && !anchor.contains(e.target)) closeWatchlistMenu(); };
  setTimeout(function(){ document.addEventListener("mousedown", menu._outside); }, 0);
}

function activeListKey(){
  var override = lsGet("activeWatchlist", null);
  if (override && STATE.watchlists.lists[override]) { lsSet("activeWatchlist", null); return override; }
  if (STATE.watchlists.active && STATE.watchlists.lists[STATE.watchlists.active] && !STATE.watchlists.lists[STATE.watchlists.active].archived) return STATE.watchlists.active;
  return activeWatchlistKeys()[0] || Object.keys(STATE.watchlists.lists)[0];
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

function activeWatchlistKeys(){ return Object.keys(STATE.watchlists.lists).filter(function(k){ return !STATE.watchlists.lists[k].archived; }); }
function deleteWatchlist(key){
  delete STATE.watchlists.lists[key];
  if (STATE.watchlists.active === key) STATE.watchlists.active = activeWatchlistKeys()[0] || null;
  saveWatchlists();
}
function openListManageMenu(anchor, key){
  closeWatchlistMenu();
  var menu = document.createElement("div"); menu.className = "wl-menu"; menu.id = "wl-menu";
  menu.innerHTML = "<div class='wm-head'>" + esc(STATE.watchlists.lists[key].label||key) + "</div>" +
    "<div class='wm-item' data-act='archive'>&#128230; Archive</div>" +
    "<div class='wm-item wm-new' data-act='delete'>&#128465; Delete permanently</div>";
  document.body.appendChild(menu);
  var r = anchor.getBoundingClientRect();
  menu.style.top = (r.bottom + window.scrollY + 4) + "px";
  menu.style.left = Math.max(8, Math.min(r.left + window.scrollX, window.scrollX + document.documentElement.clientWidth - (menu.offsetWidth||200) - 8)) + "px";
  menu.querySelector("[data-act='archive']").addEventListener("click", function(){
    STATE.watchlists.lists[key].archived = true;
    if (STATE.watchlists.active === key) STATE.watchlists.active = activeWatchlistKeys()[0] || key;
    saveWatchlists(); closeWatchlistMenu(); toast("Archived <b>" + esc(STATE.watchlists.lists[key].label||key) + "</b>"); showTab("watchlists");
  });
  menu.querySelector("[data-act='delete']").addEventListener("click", function(){
    closeWatchlistMenu();
    if (confirm("Permanently delete watchlist \"" + (STATE.watchlists.lists[key].label||key) + "\"?")){ deleteWatchlist(key); showTab("watchlists"); }
  });
  menu._outside = function(e){ if (!menu.contains(e.target) && e.target!==anchor && !anchor.contains(e.target)) closeWatchlistMenu(); };
  setTimeout(function(){ document.addEventListener("mousedown", menu._outside); }, 0);
}
function renderListChips(){
  var root = $("#wl-list-chips");
  var lists = STATE.watchlists.lists;
  var activeKeys = activeWatchlistKeys();
  var archivedKeys = Object.keys(lists).filter(function(k){ return lists[k].archived; });
  if (!activeKeys.length && !archivedKeys.length){ root.innerHTML = "<span class='muted small'>No lists yet -- clone a preset below to get started.</span>"; return; }
  var html = activeKeys.map(function(k){
    var active = k === STATE.watchlists.active;
    return "<span class='chip mgmt" + (active?" active":"") + "'><span data-list-key='" + esc(k) + "'>" + esc(lists[k].label||k) + "</span>" +
      "<span class='chip-x' data-list-menu='" + esc(k) + "' title='Manage'>&#8942;</span></span>";
  }).join("");
  if (archivedKeys.length){
    html += "<details class='archived-block'><summary>Archived (" + archivedKeys.length + ")</summary><div class='row' style='margin-top:8px'>" +
      archivedKeys.map(function(k){
        return "<span class='chip muted'>" + esc(lists[k].label||k) +
          " <button class='btn small ghost' data-list-restore='" + esc(k) + "'>Restore</button>" +
          "<button class='btn small ghost' data-list-del='" + esc(k) + "'>Delete</button></span>";
      }).join("") + "</div></details>";
  }
  root.innerHTML = html;
  $all("[data-list-key]", root).forEach(function(el){
    el.addEventListener("click", function(){ STATE.watchlists.active = el.dataset.listKey; saveWatchlists(); WL_EXPANDED = null; showTab("watchlists"); });
  });
  $all("[data-list-menu]", root).forEach(function(el){
    el.addEventListener("click", function(e){ e.stopPropagation(); openListManageMenu(el, el.dataset.listMenu); });
  });
  $all("[data-list-restore]", root).forEach(function(b){
    b.addEventListener("click", function(){ lists[b.dataset.listRestore].archived = false; saveWatchlists(); showTab("watchlists"); });
  });
  $all("[data-list-del]", root).forEach(function(b){
    b.addEventListener("click", function(){ if (confirm("Permanently delete this watchlist?")){ deleteWatchlist(b.dataset.listDel); showTab("watchlists"); } });
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
      var html = "<p class='muted small' style='margin:0 0 6px'>Click any row to open its interactive chart &amp; analytics below.</p>" +
        "<table><thead><tr><th></th><th>Ticker</th><th>Price</th><th>Chg</th><th>RSI(14)</th><th>MFI(14)</th><th>Money Flow</th><th></th></tr></thead><tbody>";
      rows.forEach(function(row){
        var isOpen = WL_EXPANDED === row.ticker;
        html += "<tr class='clickable" + (isOpen?" row-open":"") + "' data-row-ticker='" + esc(row.ticker) + "'>" +
          "<td class='caret'>" + (isOpen?"&#9662;":"&#9656;") + "</td>" +
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
          // update carets/highlight in-place, then (re)draw the chart
          $all("tr[data-row-ticker]", wrap).forEach(function(row){
            var open = row.dataset.rowTicker === WL_EXPANDED;
            row.className = "clickable" + (open?" row-open":"");
            var caret = row.querySelector(".caret"); if (caret) caret.innerHTML = open?"&#9662;":"&#9656;";
          });
          renderWatchlistChart(list);
          var chartEl = $("#wl-chart-wrap");
          if (WL_EXPANDED && chartEl) chartEl.scrollIntoView({behavior:"smooth", block:"nearest"});
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
    "<div class='card' style='margin-top:14px'>" +
      "<div class='flex-between'>" +
        "<h3 style='margin:0;color:var(--text);text-transform:none;font-size:16px'>" + esc(ticker) + " &mdash; trend &amp; analytics</h3>" +
        "<button class='btn small ghost' id='wl-open-companies'>Open full analytics &rarr;</button>" +
      "</div>" +
      "<div id='wl-metrics' class='adv-readout' style='margin-top:8px'></div>" +
      "<div id='wl-adv-chart' style='margin-top:6px'></div>" +
    "</div>";
  $("#wl-open-companies").addEventListener("click", function(){
    CO_TICKER = ticker; lsSet("companiesTicker", ticker); showTab("companies");
  });
  getSeries(ticker).then(function(s){
    renderCompactMetrics($("#wl-metrics"), s);
    var ind = list.indicators || {};
    var stateKey = "advChart_watchlist";
    if (!lsGet(stateKey, null)){
      lsSet(stateKey, {range:"1Y", type:"candles",
        overlays:{sma20:!!ind.sma, sma50:false, sma200:false, ema21:!!ind.ema, bb:!!ind.bollinger, vwap:!!ind.vwap},
        osc: ind.macd ? "macd" : "rsi"});
    }
    renderAdvancedChart($("#wl-adv-chart"), ticker, s, stateKey);
  });
}

// compact analytics strip reused by the watchlist expansion
function renderCompactMetrics(root, s){
  if (!root) return;
  var closes = s.closes, dates = s.dates, volumes = s.volumes;
  var price = closes[closes.length-1];
  var chg = closes.length>1 ? ((price/closes[closes.length-2])-1)*100 : null;
  var rsi = IND.rsi(dates, closes, 14); var rsiVal = rsi[rsi.length-1].p;
  var mfi = IND.mfi(dates, closes, volumes, 14); var mfiVal = mfi[mfi.length-1].p;
  var status = IND.moneyFlowStatus(IND.cmf(dates, closes, volumes, 21), 21);
  var oneY = closes.length>=252 ? ((price/closes[closes.length-252])-1)*100 : ((price/closes[0])-1)*100;
  var w52 = closes.slice(-252); var hi=Math.max.apply(null,w52), lo=Math.min.apply(null,w52);
  root.innerHTML =
    "<span>Price <b>" + fmtPrice(price) + "</b></span>" +
    "<span class='" + pctClass(chg) + "'>" + fmtPct(chg) + " today</span>" +
    "<span>RSI <b>" + fmtNum(rsiVal,1) + "</b></span>" +
    "<span>MFI <b>" + fmtNum(mfiVal,1) + "</b></span>" +
    "<span>Flow <span class='pill " + status.cls + "'>" + status.label + "</span></span>" +
    "<span>1Y <b class='" + pctClass(oneY) + "'>" + fmtPct(oneY) + "</b></span>" +
    "<span class='muted'>52W " + fmtPrice(lo) + "&ndash;" + fmtPrice(hi) + "</span>";
}
"""

JS_CHART = r"""
// ---- Advanced Yahoo-style chart component -------------------------------
// Candlesticks are drawn with Chart.js floating bars (grouped:false so wick +
// body center on the same category slot) -- no financial plugin needed, and it
// stays on the same category x-axis used everywhere else in the app.
var GRID = "#1b2536", AXIS = "#93a2bb", UP = "#3ecf8e", DOWN = "#f56565";
var ADV_RANGES = [["1M",21],["3M",63],["6M",126],["YTD",-1],["1Y",252],["2Y",504],["Max",99999]];
var ADV_OVERLAYS = [["sma20","SMA 20","#f6ad55"],["sma50","SMA 50","#5b8cff"],["sma200","SMA 200","#a78bfa"],["ema21","EMA 21","#22d3ee"],["bb","Bollinger","#93a2bb"],["vwap","VWAP","#f472b6"]];
var ADV_OSC = [["rsi","RSI"],["macd","MACD"],["mfi","MFI"],["cmf","CMF"]];

var crosshairPlugin = {
  id: "gmrCrosshair",
  afterDatasetsDraw: function(chart){
    var idx = chart.$hoverIndex;
    if (idx == null) return;
    var x = chart.scales.x.getPixelForValue(idx);
    if (x == null || isNaN(x)) return;
    var a = chart.chartArea, ctx = chart.ctx;
    ctx.save();
    ctx.beginPath(); ctx.moveTo(x, a.top); ctx.lineTo(x, a.bottom);
    ctx.lineWidth = 1; ctx.strokeStyle = "rgba(147,162,187,.45)"; ctx.setLineDash([4,3]); ctx.stroke();
    ctx.restore();
  }
};

// draws the translucent drag-to-zoom selection rectangle
var dragPlugin = {
  id: "gmrDrag",
  afterDatasetsDraw: function(chart){
    var r = chart.$dragRect;
    if (!r) return;
    var a = chart.chartArea, ctx = chart.ctx;
    var x1 = Math.max(a.left, Math.min(r.x1, r.x2)), x2 = Math.min(a.right, Math.max(r.x1, r.x2));
    ctx.save();
    ctx.fillStyle = "rgba(79,209,197,.14)";
    ctx.strokeStyle = "rgba(79,209,197,.6)";
    ctx.lineWidth = 1;
    ctx.fillRect(x1, a.top, x2-x1, a.bottom-a.top);
    ctx.beginPath(); ctx.moveTo(x1, a.top); ctx.lineTo(x1, a.bottom); ctx.moveTo(x2, a.top); ctx.lineTo(x2, a.bottom); ctx.stroke();
    ctx.restore();
  }
};

function advLine(label, arr, color, opts){
  var ds = { type:"line", label:label, data:arr.map(function(x){return x.p;}), borderColor:color, pointRadius:0, borderWidth:1.3, tension:.1, order:0 };
  if (opts) Object.keys(opts).forEach(function(k){ ds[k]=opts[k]; });
  return ds;
}

// renderAdvancedChart(root, ticker, fullSeries, stateKey)
function renderAdvancedChart(root, ticker, fullSeries, stateKey){
  if (!root) return; // container gone (user navigated away before data loaded)
  var state = lsGet(stateKey, {range:"1Y", type:"candles", overlays:{sma20:true, sma50:true, sma200:false, ema21:false, bb:false, vwap:false}, osc:"rsi"});
  state.overlays = state.overlays || {};
  var ctx = { root:root, ticker:ticker, series:fullSeries, state:state, stateKey:stateKey, charts:{}, zoom:null };

  root.innerHTML =
    "<div class='chart-toolbar'>" +
      "<div class='seg' id='adv-range'>" + ADV_RANGES.map(function(r){ return "<button data-range='" + r[0] + "'" + (state.range===r[0]?" class='on'":"") + ">" + r[0] + "</button>"; }).join("") + "</div>" +
      "<div class='seg' id='adv-type'>" + [["candles","Candles"],["area","Area"],["line","Line"]].map(function(t){ return "<button data-type='" + t[0] + "'" + (state.type===t[0]?" class='on'":"") + ">" + t[1] + "</button>"; }).join("") + "</div>" +
      "<button class='btn small ghost hidden' id='adv-reset-zoom'>&#10227; Reset zoom</button>" +
      "<span class='muted small zoom-hint' style='align-self:center'>Two-finger scroll to zoom &middot; drag to pan &middot; double-click to reset</span>" +
    "</div>" +
    "<div class='chart-toolbar'>" +
      "<span class='muted small' style='align-self:center'>Overlays:</span>" +
      "<div class='seg' id='adv-overlays'>" + ADV_OVERLAYS.map(function(o){ return "<button data-ov='" + o[0] + "'" + (state.overlays[o[0]]?" class='on'":"") + ">" + o[1] + "</button>"; }).join("") + "</div>" +
    "</div>" +
    "<div class='adv-readout' id='adv-readout'></div>" +
    "<div class='chart-wrap' style='height:300px'><canvas id='adv-price'></canvas></div>" +
    "<div class='chart-wrap' style='height:90px'><canvas id='adv-volume'></canvas></div>" +
    "<div class='chart-toolbar' style='margin-top:6px'>" +
      "<span class='muted small' style='align-self:center'>Lower pane:</span>" +
      "<div class='seg' id='adv-osc'>" + ADV_OSC.map(function(o){ return "<button data-osc='" + o[0] + "'" + (state.osc===o[0]?" class='on'":"") + ">" + o[1] + "</button>"; }).join("") + "</div>" +
    "</div>" +
    "<div class='chart-wrap' style='height:130px'><canvas id='adv-osc-canvas'></canvas></div>";

  function saveState(){ lsSet(stateKey, state); }
  function bindSeg(sel, attr, cb){
    $all(sel + " button", root).forEach(function(b){
      b.addEventListener("click", function(){
        cb(b.getAttribute(attr), b);
      });
    });
  }
  bindSeg("#adv-range", "data-range", function(v){ state.range=v; ctx.zoom=null; saveState(); $all("#adv-range button",root).forEach(function(x){x.className=(x.getAttribute("data-range")===v)?"on":"";}); drawAdvanced(ctx); });
  bindSeg("#adv-type", "data-type", function(v){ state.type=v; saveState(); $all("#adv-type button",root).forEach(function(x){x.className=(x.getAttribute("data-type")===v)?"on":"";}); drawAdvanced(ctx); });
  bindSeg("#adv-overlays", "data-ov", function(v,b){ state.overlays[v]=!state.overlays[v]; saveState(); b.className=state.overlays[v]?"on":""; drawAdvanced(ctx); });
  bindSeg("#adv-osc", "data-osc", function(v){ state.osc=v; saveState(); $all("#adv-osc button",root).forEach(function(x){x.className=(x.getAttribute("data-osc")===v)?"on":"";}); drawAdvanced(ctx); });
  $("#adv-reset-zoom", root).addEventListener("click", function(){ ctx.zoom=null; drawAdvanced(ctx); });

  drawAdvanced(ctx);
  wireInteractionsOnce(ctx);
}

// Absolute index window for the current view: honors a drag-zoom window if set,
// otherwise the selected range button. Returns {start, slice}.
function computeView(ctx){
  var series = ctx.series, n = series.closes.length;
  var start, end;
  if (ctx.zoom){
    start = Math.max(0, ctx.zoom.start);
    end = Math.min(n-1, ctx.zoom.end);
  } else {
    end = n-1;
    var range = ctx.state.range;
    if (range === "Max") start = 0;
    else if (range === "YTD"){
      var y = new Date().getFullYear();
      start = series.dates.findIndex(function(d){ return d >= (y + "-01-01"); });
      if (start < 0) start = 0;
    } else {
      var days = 252; ADV_RANGES.forEach(function(r){ if(r[0]===range) days=r[1]; });
      start = Math.max(0, n - days);
    }
  }
  function sl(a){ return a ? a.slice(start, end+1) : null; }
  return { start:start, slice:{ dates:sl(series.dates), opens:sl(series.opens), highs:sl(series.highs), lows:sl(series.lows), closes:sl(series.closes), volumes:sl(series.volumes), synthetic:series.synthetic } };
}

function baseAxes(showX){
  return {
    x: { grid:{color:GRID, display:false}, ticks:{color:AXIS, maxTicksLimit:8, display:!!showX, maxRotation:0, autoSkip:true}, offset:false },
    y: { position:"right", grid:{color:GRID}, ticks:{color:AXIS} }
  };
}

function drawAdvanced(ctx){
  var view = computeView(ctx);
  ctx.viewStart = view.start;
  var s = view.slice;
  var labels = s.dates;
  var st = ctx.state;
  var resetBtn = $("#adv-reset-zoom", ctx.root);
  if (resetBtn) resetBtn.className = "btn small ghost" + (ctx.zoom ? "" : " hidden");
  Object.keys(ctx.charts).forEach(function(k){ if(ctx.charts[k]) ctx.charts[k].destroy(); });

  var colorByDir = s.closes.map(function(c,i){ return c >= s.opens[i] ? UP : DOWN; });

  // ---- price ----
  var priceDs = [];
  if (st.type === "candles"){
    priceDs.push({ type:"bar", label:"wick", data:s.highs.map(function(h,i){return [s.lows[i], h];}), backgroundColor:colorByDir, barThickness:1.2, grouped:false, order:5 });
    priceDs.push({ type:"bar", label:"body", data:s.closes.map(function(c,i){return [s.opens[i], c];}), backgroundColor:colorByDir, borderColor:colorByDir, maxBarThickness:9, grouped:false, order:4 });
  } else if (st.type === "area"){
    priceDs.push({ type:"line", label:ctx.ticker, data:s.closes, borderColor:"#4fd1c5", backgroundColor:"rgba(79,209,197,.12)", fill:true, pointRadius:0, borderWidth:1.7, tension:.1 });
  } else {
    priceDs.push({ type:"line", label:ctx.ticker, data:s.closes, borderColor:"#4fd1c5", pointRadius:0, borderWidth:1.7, tension:.1 });
  }
  var ov = st.overlays;
  if (ov.sma20) priceDs.push(advLine("SMA 20", IND.sma(labels,s.closes,20), "#f6ad55"));
  if (ov.sma50) priceDs.push(advLine("SMA 50", IND.sma(labels,s.closes,50), "#5b8cff"));
  if (ov.sma200) priceDs.push(advLine("SMA 200", IND.sma(labels,s.closes,200), "#a78bfa"));
  if (ov.ema21) priceDs.push(advLine("EMA 21", IND.ema(labels,s.closes,21), "#22d3ee"));
  if (ov.vwap) priceDs.push(advLine("VWAP", IND.vwap(labels,s.closes,s.volumes), "#f472b6"));
  if (ov.bb){
    var b = IND.bollinger(labels, s.closes, 20, 2);
    priceDs.push(advLine("BB Up", b.upper, "rgba(147,162,187,.7)", {borderDash:[4,3]}));
    priceDs.push(advLine("BB Low", b.lower, "rgba(147,162,187,.7)", {borderDash:[4,3]}));
  }
  ctx.charts.price = new Chart($("#adv-price", ctx.root).getContext("2d"), {
    type:"bar",
    data:{ labels:labels, datasets:priceDs },
    options:{
      maintainAspectRatio:false, animation:false,
      scales:{ x: baseAxes(false).x, y:{ position:"right", grid:{color:GRID}, ticks:{color:AXIS} } },
      plugins:{ legend:{ display:st.type!=="candles", labels:{color:AXIS, boxWidth:10, filter:function(l){return l.text!=="wick"&&l.text!=="body";}} }, tooltip:{ enabled:false } }
    },
    plugins:[crosshairPlugin, dragPlugin]
  });

  // ---- volume ----
  ctx.charts.volume = new Chart($("#adv-volume", ctx.root).getContext("2d"), {
    type:"bar",
    data:{ labels:labels, datasets:[{ label:"Volume", data:s.volumes, backgroundColor:colorByDir.map(function(c){return c===UP?"rgba(62,207,142,.55)":"rgba(245,101,101,.55)";}), barThickness:"flex", categoryPercentage:1, barPercentage:.9 }] },
    options:{ maintainAspectRatio:false, animation:false,
      scales:{ x:{ grid:{display:false}, ticks:{display:false} }, y:{ position:"right", grid:{color:GRID}, ticks:{color:AXIS, maxTicksLimit:3, callback:function(v){ return v>=1e6?(v/1e6).toFixed(0)+"M":(v/1e3).toFixed(0)+"K"; }} } },
      plugins:{ legend:{display:false}, tooltip:{enabled:false} } },
    plugins:[crosshairPlugin, dragPlugin]
  });

  // ---- oscillator ----
  drawOsc(ctx, s, labels);

  // interactions are wired once to the persistent canvas elements (see
  // wireInteractionsOnce); here we just record the current slice + readout.
  ctx.curSlice = s;
  updateReadout(ctx, s, s.closes.length-1);
}

function drawOsc(ctx, s, labels){
  var canvas = $("#adv-osc-canvas", ctx.root);
  var osc = ctx.state.osc;
  var ds = [], yOpts = { position:"right", grid:{color:GRID}, ticks:{color:AXIS, maxTicksLimit:4} }, ann = [];
  if (osc === "rsi"){
    ds = [advLine("RSI 14", IND.rsi(labels,s.closes,14), "#a78bfa")];
    yOpts.min = 0; yOpts.max = 100;
  } else if (osc === "mfi"){
    ds = [advLine("MFI 14", IND.mfi(labels,s.closes,s.volumes,14), "#22d3ee")];
    yOpts.min = 0; yOpts.max = 100;
  } else if (osc === "cmf"){
    ds = [advLine("CMF 21", IND.cmf(labels,s.closes,s.volumes,21), "#4fd1c5")];
    yOpts.min = -1; yOpts.max = 1;
  } else {
    var m = IND.macd(labels, s.closes);
    ds = [
      { type:"bar", label:"Hist", data:m.hist.map(function(x){return x.p;}), backgroundColor:m.hist.map(function(x){return (x.p||0)>=0?"rgba(62,207,142,.5)":"rgba(245,101,101,.5)";}), barThickness:"flex", categoryPercentage:1, barPercentage:.9, order:3 },
      advLine("MACD", m.line, "#4fd1c5"),
      advLine("Signal", m.signal, "#f6ad55")
    ];
  }
  ctx.charts.osc = new Chart(canvas.getContext("2d"), {
    type:"bar", data:{ labels:labels, datasets:ds },
    options:{ maintainAspectRatio:false, animation:false,
      scales:{ x:{ grid:{color:GRID, display:false}, ticks:{color:AXIS, maxTicksLimit:8, maxRotation:0} }, y:yOpts },
      plugins:{ legend:{ labels:{color:AXIS, boxWidth:10} }, tooltip:{enabled:false} } },
    plugins:[crosshairPlugin, dragPlugin]
  });
}

// Bound ONCE per renderAdvancedChart to the persistent canvas elements, so
// pan/zoom state survives the chart redraws (which destroy + recreate the Chart
// instances but leave the <canvas> elements intact). Interactions:
//   - two-finger vertical scroll (wheel) => zoom in/out around the cursor
//   - horizontal drag                     => pan the visible date window
//   - double-click                        => reset to the selected range
function wireInteractionsOnce(ctx){
  var n = ctx.series.closes.length;
  var roles = ["price","volume","osc"];
  var ids = {price:"#adv-price", volume:"#adv-volume", osc:"#adv-osc-canvas"};
  var pan = null, rafPending = false, pendingWin = null;

  function allCharts(){ return [ctx.charts.price, ctx.charts.volume, ctx.charts.osc].filter(Boolean); }
  function curWin(){ var len = ctx.curSlice.closes.length; return {start:ctx.viewStart, end:ctx.viewStart+len-1, len:len}; }
  function clampWin(start, end){
    start = Math.round(start); end = Math.round(end);
    if (start < 0){ end -= start; start = 0; }
    if (end > n-1){ start -= (end-(n-1)); end = n-1; }
    return {start:Math.max(0,start), end:Math.min(n-1,end)};
  }
  function applyWin(start, end){
    var w = clampWin(start, end);
    if (w.end - w.start < 4) return;
    ctx.zoom = (w.start === 0 && w.end === n-1) ? null : {start:w.start, end:w.end};
    drawAdvanced(ctx);
  }
  function applyWinThrottled(start, end){
    pendingWin = [start, end];
    if (rafPending) return;
    rafPending = true;
    requestAnimationFrame(function(){ rafPending = false; if (pendingWin){ applyWin(pendingWin[0], pendingWin[1]); pendingWin = null; } });
  }
  function localIdx(chart, clientX){
    var rect = chart.canvas.getBoundingClientRect();
    var idx = Math.round(chart.scales.x.getValueForPixel(clientX - rect.left));
    return Math.max(0, Math.min(ctx.curSlice.closes.length-1, idx));
  }
  function hover(clientX){
    var cs = allCharts(); if (!cs.length) return;
    var idx = localIdx(cs[0], clientX);
    cs.forEach(function(c){ c.$hoverIndex = idx; c.update("none"); });
    updateReadout(ctx, ctx.curSlice, idx);
  }
  function onPanMove(e){
    if (!pan) return;
    var chart = ctx.charts[pan.role]; if (!chart) return;
    var a = chart.chartArea;
    var winLen = pan.winEnd - pan.winStart + 1;
    var barPx = (a.right - a.left) / Math.max(1, winLen);
    var dxBars = Math.round((e.clientX - pan.startX) / barPx);
    applyWinThrottled(pan.winStart - dxBars, pan.winEnd - dxBars);
  }
  function onPanUp(){
    pan = null;
    window.removeEventListener("mousemove", onPanMove);
    window.removeEventListener("mouseup", onPanUp);
  }

  roles.forEach(function(role){
    var cv = $(ids[role], ctx.root);
    if (!cv) return;
    cv.style.cursor = "grab";
    cv.addEventListener("mousedown", function(e){
      var w = curWin();
      pan = {role:role, startX:e.clientX, winStart:w.start, winEnd:w.end};
      e.preventDefault();
      window.addEventListener("mousemove", onPanMove);
      window.addEventListener("mouseup", onPanUp);
    });
    cv.addEventListener("mousemove", function(e){ if (!pan) hover(e.clientX); });
    cv.addEventListener("mouseleave", function(){
      if (pan) return;
      allCharts().forEach(function(c){ c.$hoverIndex = null; c.update("none"); });
      updateReadout(ctx, ctx.curSlice, ctx.curSlice.closes.length-1);
    });
    cv.addEventListener("dblclick", function(){ if (ctx.zoom){ ctx.zoom = null; drawAdvanced(ctx); } });
    cv.addEventListener("wheel", function(e){
      e.preventDefault();
      var chart = ctx.charts[role]; if (!chart) return;
      var w = curWin();
      var focus = w.start + localIdx(chart, e.clientX);
      var factor = e.deltaY < 0 ? 0.85 : 1.18;   // scroll up = zoom in
      var newLen = Math.max(6, Math.min(n, Math.round(w.len * factor)));
      var rel = (focus - w.start) / Math.max(1, w.len);
      var ns = Math.round(focus - rel * newLen);
      applyWin(ns, ns + newLen - 1);
    }, {passive:false});
    // touch: single-finger horizontal pan
    cv.addEventListener("touchstart", function(e){ if (e.touches.length===1){ var w=curWin(); pan={role:role, startX:e.touches[0].clientX, winStart:w.start, winEnd:w.end}; } }, {passive:true});
    cv.addEventListener("touchmove", function(e){
      if (pan && e.touches.length===1){
        var chart=ctx.charts[pan.role]; if(!chart) return;
        var a=chart.chartArea; var winLen=pan.winEnd-pan.winStart+1; var barPx=(a.right-a.left)/Math.max(1,winLen);
        var dxBars=Math.round((e.touches[0].clientX-pan.startX)/barPx);
        applyWinThrottled(pan.winStart-dxBars, pan.winEnd-dxBars);
        e.preventDefault();
      } else if (e.touches[0]) { hover(e.touches[0].clientX); }
    }, {passive:false});
    cv.addEventListener("touchend", function(){ pan = null; });
  });
}

function updateReadout(ctx, s, i){
  var el = $("#adv-readout", ctx.root);
  if (!el || i==null || i<0 || i>=s.closes.length) return;
  var o=s.opens[i], h=s.highs[i], l=s.lows[i], c=s.closes[i], v=s.volumes[i];
  var prev = i>0 ? s.closes[i-1] : o;
  var chg = prev ? ((c/prev)-1)*100 : 0;
  var volStr = v>=1e6 ? (v/1e6).toFixed(2)+"M" : (v/1e3).toFixed(0)+"K";
  el.innerHTML =
    "<span class='ro-date'>" + esc(s.dates[i]) + "</span>" +
    "<span>O <b>" + fmtNum(o,2) + "</b></span>" +
    "<span>H <b>" + fmtNum(h,2) + "</b></span>" +
    "<span>L <b>" + fmtNum(l,2) + "</b></span>" +
    "<span>C <b>" + fmtNum(c,2) + "</b></span>" +
    "<span class='" + pctClass(chg) + "'>" + fmtPct(chg) + "</span>" +
    "<span class='muted'>Vol " + volStr + "</span>";
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

function maxDrawdown(closes){
  var peak = -Infinity, mdd = 0;
  for (var i=0;i<closes.length;i++){
    peak = Math.max(peak, closes[i]);
    var dd = (closes[i]/peak) - 1;
    if (dd < mdd) mdd = dd;
  }
  return mdd*100;
}

function renderCompanyDetail(){
  var root = $("#co-detail");
  root.innerHTML = "<div class='card'><p class='muted small'>Loading " + esc(CO_TICKER) + "...</p></div>";
  getSeries(CO_TICKER).then(function(s){
    var closes = s.closes, dates = s.dates, volumes = s.volumes;
    var price = closes[closes.length-1];
    var chg = closes.length>1 ? ((price/closes[closes.length-2])-1)*100 : null;
    var chgAbs = closes.length>1 ? (price - closes[closes.length-2]) : null;
    var window52 = closes.slice(-252);
    var hi52 = Math.max.apply(null, window52), lo52 = Math.min.apply(null, window52);
    var dayHi = s.highs ? s.highs[s.highs.length-1] : price, dayLo = s.lows ? s.lows[s.lows.length-1] : price;
    var pos52 = (hi52>lo52) ? ((price-lo52)/(hi52-lo52))*100 : 50;
    var avgVol = volumes.slice(-20).reduce(function(a,b){return a+b;},0) / Math.max(1, volumes.slice(-20).length);
    var rsi = IND.rsi(dates, closes, 14); var rsiVal = rsi[rsi.length-1].p;
    var mfi = IND.mfi(dates, closes, volumes, 14); var mfiVal = mfi[mfi.length-1].p;
    var cmf = IND.cmf(dates, closes, volumes, 21);
    var status = IND.moneyFlowStatus(cmf, 21);
    var sma200 = IND.sma(dates, closes, 200); var sma200Val = sma200[sma200.length-1].p;
    var vs200 = sma200Val ? ((price/sma200Val)-1)*100 : null;
    var ytdIdx = dates.findIndex(function(d){ return d >= (new Date().getFullYear() + "-01-01"); });
    var ytdReturn = ytdIdx > 0 ? ((price/closes[ytdIdx])-1)*100 : null;
    var oneYReturn = closes.length>=252 ? ((price/closes[closes.length-252])-1)*100 : ((price/closes[0])-1)*100;
    var rets = []; for (var i=1;i<closes.length;i++) rets.push(closes[i]/closes[i-1]-1);
    var meanRet = rets.reduce(function(a,b){return a+b;},0)/rets.length;
    var variance = rets.reduce(function(a,b){return a+Math.pow(b-meanRet,2);},0)/rets.length;
    var annVol = Math.sqrt(variance*252)*100;
    var mdd = maxDrawdown(closes);
    var f = s.fundamentals || {};
    var name = f.name || tickerName(CO_TICKER);
    var updatedNote = s.updated ? ("Data as of " + esc(s.updated.slice(0,10))) : "";
    var exch = f.exchange ? esc(f.exchange) : "";

    // Yahoo-style stats grid. Prefer baked fundamentals; fall back to values
    // derived from the OHLCV series so proxy/synthetic tickers still populate.
    function stat(lbl, val){ return "<div class='stat-row'><span class='lbl'>" + lbl + "</span><span class='val'>" + val + "</span></div>"; }
    var prevClose = f.previousClose != null ? f.previousClose : (closes.length>1?closes[closes.length-2]:price);
    var openV = f.open != null ? f.open : (s.opens?s.opens[s.opens.length-1]:null);
    var dRangeLo = f.dayLow != null ? f.dayLow : dayLo, dRangeHi = f.dayHigh != null ? f.dayHigh : dayHi;
    var w52lo = f.fiftyTwoWeekLow != null ? f.fiftyTwoWeekLow : lo52, w52hi = f.fiftyTwoWeekHigh != null ? f.fiftyTwoWeekHigh : hi52;
    var volNow = f.volume != null ? f.volume : volumes[volumes.length-1];
    var avgV = f.avgVolume != null ? f.avgVolume : avgVol;
    var divStr = (f.dividendRate != null) ? (fmtNum(f.dividendRate,2) + (f.dividendYield!=null?(" (" + fmtNum(f.dividendYield*100,2) + "%)"):"")) : "--";

    var statsGrid =
      "<div class='stats-grid'>" +
        "<div>" +
          stat("Previous Close", fmtNum(prevClose,2)) +
          stat("Open", openV!=null?fmtNum(openV,2):"--") +
          stat("Bid", f.bid!=null?fmtNum(f.bid,2):"--") +
          stat("Ask", f.ask!=null?fmtNum(f.ask,2):"--") +
        "</div>" +
        "<div>" +
          stat("Day&#39;s Range", fmtNum(dRangeLo,2) + " - " + fmtNum(dRangeHi,2)) +
          stat("52 Week Range", fmtNum(w52lo,2) + " - " + fmtNum(w52hi,2)) +
          stat("Volume", fmtInt(volNow)) +
          stat("Avg. Volume", fmtInt(avgV)) +
        "</div>" +
        "<div>" +
          stat("Market Cap", fmtBig(f.marketCap)) +
          stat("Beta (5Y)", f.beta!=null?fmtNum(f.beta,2):"--") +
          stat("PE Ratio (TTM)", f.trailingPE!=null?fmtNum(f.trailingPE,2):"--") +
          stat("EPS (TTM)", f.trailingEps!=null?fmtNum(f.trailingEps,2):"--") +
        "</div>" +
        "<div>" +
          stat("Earnings Date", fmtDateTs(f.earningsDate)) +
          stat("Fwd Div &amp; Yield", divStr) +
          stat("Ex-Dividend Date", fmtDateTs(f.exDividendDate)) +
          stat("1y Target Est", f.targetMeanPrice!=null?fmtNum(f.targetMeanPrice,2):"--") +
        "</div>" +
      "</div>";

    var overview = "";
    if (!(f.summary || f.sector || f.industry)){
      // non-baked ticker: real price/chart, but fundamentals need the baked set
      overview =
        "<p class='footer-note' style='margin-top:10px'>Price, chart, and technicals above are live. Full fundamentals " +
        "(market cap, P/E, EPS, company profile) are baked for tracked tickers &mdash; add <b>" + esc(CO_TICKER) + "</b> to a " +
        "watchlist and Arm alerts, and it&#39;ll be included in the next data refresh.</p>";
    } else {
      overview =
        "<div class='section-title'>" + esc(name) + " Overview</div>" +
        "<div class='overview'>" +
          "<div><p class='small' style='line-height:1.5'>" + esc(f.summary||"") + "</p>" +
            (f.website ? "<p><a href='" + esc(f.website) + "' target='_blank' rel='noopener'>" + esc(f.website.replace(/^https?:\/\//,"")) + "</a></p>" : "") + "</div>" +
          "<div class='prof'>" +
            "<div><div class='big'>" + (f.employees!=null?fmtInt(f.employees):"--") + "</div><div class='sub'>Full-Time Employees</div></div>" +
            "<div><div class='big'>" + (f.sharesOutstanding!=null?fmtBig(f.sharesOutstanding):"--") + "</div><div class='sub'>Shares Outstanding</div></div>" +
            "<div><div class='big'>" + esc(f.sector||"--") + "</div><div class='sub'>Sector</div></div>" +
            "<div><div class='big'>" + esc(f.industry||"--") + "</div><div class='sub'>Industry</div></div>" +
          "</div>" +
        "</div>";
    }

    root.innerHTML =
      "<div class='card'>" +
        "<div class='flex-between'>" +
          "<div><h2>" + esc(CO_TICKER) + (exch?" <span class='tag'>" + exch + "</span>":"") + (s.synthetic ? " <span class='tag'>sample data</span>" : "") + "</h2>" +
            "<p class='muted small'>" + esc(name) + (updatedNote ? " &middot; " + updatedNote : "") + "</p></div>" +
          "<div style='text-align:right'>" +
            "<div style='font-size:28px;font-weight:800'>" + fmtPrice(price) + "</div>" +
            "<div class='" + pctClass(chg) + "'>" + (chgAbs!=null?(chgAbs>=0?"+":"")+fmtNum(chgAbs,2):"--") + " (" + fmtPct(chg) + ") today</div>" +
          "</div>" +
        "</div>" +
        "<div id='co-adv-chart' style='margin-top:14px'></div>" +
        "<div class='cta-row'><button class='btn small ghost' id='co-add-to-list'>+ Add " + esc(CO_TICKER) + " to watchlist &#9662;</button></div>" +
        "<div class='section-title'>Statistics</div>" +
        statsGrid +
        overview +
        "<div class='section-title'>Technicals &amp; Performance</div>" +
        "<div class='grid cols-4'>" +
          "<div class='card'><h3>Money Flow</h3><div><span class='pill " + status.cls + "'>" + status.label + "</span></div></div>" +
          "<div class='card'><h3>RSI(14)</h3><div class='" + (rsiVal>70?"down":(rsiVal<30?"up":"")) + "'>" + fmtNum(rsiVal,1) + "</div></div>" +
          "<div class='card'><h3>MFI(14)</h3><div class='" + (mfiVal>80?"down":(mfiVal<20?"up":"")) + "'>" + fmtNum(mfiVal,1) + "</div></div>" +
          "<div class='card'><h3>Price vs SMA200</h3><div class='" + pctClass(vs200) + "'>" + fmtPct(vs200) + "</div></div>" +
          "<div class='card'><h3>Annualized Vol</h3><div>" + fmtNum(annVol,1) + "%</div></div>" +
          "<div class='card'><h3>YTD Return</h3><div class='" + pctClass(ytdReturn) + "'>" + fmtPct(ytdReturn) + "</div></div>" +
          "<div class='card'><h3>1Y Return</h3><div class='" + pctClass(oneYReturn) + "'>" + fmtPct(oneYReturn) + "</div></div>" +
          "<div class='card'><h3>Max Drawdown (2Y)</h3><div class='down'>" + fmtNum(mdd,1) + "%</div></div>" +
        "</div>" +
      "</div>";

    // scope queries to the captured root so a mid-load tab switch (root
    // detached) resolves them on the detached subtree instead of returning null
    renderAdvancedChart($("#co-adv-chart", root), CO_TICKER, s, "advChart_companies");

    var addBtn = $("#co-add-to-list", root);
    if (addBtn) addBtn.addEventListener("click", function(e){
      e.stopPropagation();
      openWatchlistMenu(addBtn, CO_TICKER, function(key, list){ addBtn.textContent = "Added to " + (list.label||key); });
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

var CO_COMPARE_CHART = null;
function renderCompareChart(){
  var canvas = $("#co-compare-canvas");
  var tableRoot = $("#co-compare-table");
  if (!canvas) return;
  if (CO_COMPARE_CHART){ CO_COMPARE_CHART.destroy(); CO_COMPARE_CHART = null; }
  if (!CO_COMPARE.length){ tableRoot.innerHTML=""; return; }
  var colors = ["#4fd1c5","#f6ad55","#5b8cff","#3ecf8e","#f56565","#a78bfa","#f472b6"];
  Promise.all(CO_COMPARE.map(function(t){ return getSeries(t); })).then(function(seriesList){
    if (!$("#co-compare-canvas")) return; // navigated away
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
    if (CO_COMPARE_CHART) CO_COMPARE_CHART.destroy();
    CO_COMPARE_CHART = new Chart(canvas.getContext("2d"), {
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
  var html = "<div class='flex-between'><h3 style='margin:0'>Weights for Selected Mix</h3>" +
      "<div class='row'><button class='btn small ghost' id='opt-save-index'>Save as index</button>" +
      "<button class='btn small' id='opt-save-wl'>Save as watchlist &#9662;</button></div></div>" +
    "<div class='grid cols-3' style='margin:12px 0 14px'>" +
      "<div class='card'><h3>Expected Return</h3><div class='" + pctClass(p.ret*100) + "'>" + fmtPct(p.ret*100) + "</div></div>" +
      "<div class='card'><h3>Volatility</h3><div>" + fmtNum(p.vol*100,1) + "%</div></div>" +
      "<div class='card'><h3>Sharpe</h3><div>" + fmtNum(p.sharpe,2) + "</div></div>" +
    "</div>" +
    "<table><thead><tr><th>Ticker</th><th>Weight</th><th></th></tr></thead><tbody>";
  rows.forEach(function(r){
    if (r.weight < 0.001) return;
    html += "<tr class='clickable' data-opt-ticker='" + esc(r.ticker) + "'><td>" + esc(r.ticker) + "</td><td>" + fmtNum(r.weight*100,1) + "%</td>" +
      "<td><button class='btn small ghost' data-opt-add='" + esc(r.ticker) + "'>+ Watchlist</button></td></tr>";
  });
  html += "</tbody></table>";
  root.innerHTML = html;

  // per-ticker: open Companies on row click, add via picker on the button
  $all("[data-opt-ticker]", root).forEach(function(tr){
    tr.addEventListener("click", function(){ CO_TICKER = tr.dataset.optTicker; lsSet("companiesTicker", CO_TICKER); showTab("companies"); });
  });
  $all("[data-opt-add]", root).forEach(function(b){
    b.addEventListener("click", function(e){ e.stopPropagation(); openWatchlistMenu(b, b.dataset.optAdd, function(){ b.textContent = "Added"; }); });
  });
  // bulk: save the whole optimized set
  var activeTickers = rows.filter(function(r){ return r.weight >= 0.001; }).map(function(r){ return r.ticker; });
  var weightMap = {}; rows.forEach(function(r){ if (r.weight>=0.001) weightMap[r.ticker] = Math.round(r.weight*1000)/10; });
  $("#opt-save-wl").addEventListener("click", function(e){
    e.stopPropagation();
    saveTickersAsWatchlist($("#opt-save-wl"), activeTickers);
  });
  $("#opt-save-index").addEventListener("click", function(){
    var name = prompt("Name this index (optimized portfolio):", (OPT_UNIVERSE_KEY||"Optimized") + " Index");
    if (!name) return;
    createIndexFromWeights(name.trim(), activeTickers, weightMap);
    toast("Created index <b>" + esc(name.trim()) + "</b> -- see the Indexes tab");
  });
}

// Save a set of tickers into a chosen (or new) watchlist via the picker.
function saveTickersAsWatchlist(anchor, tickers){
  closeWatchlistMenu();
  var menu = document.createElement("div");
  menu.className = "wl-menu"; menu.id = "wl-menu";
  var lists = STATE.watchlists.lists || {};
  var rows = Object.keys(lists).map(function(k){
    return "<div class='wm-item' data-bulk-wl='" + esc(k) + "'><span>" + esc(lists[k].label||k) + "</span><span class='wm-meta'>" + (lists[k].tickers||[]).length + " names</span></div>";
  }).join("");
  menu.innerHTML = "<div class='wm-head'>Save " + tickers.length + " names to</div>" + rows + "<div class='wm-item wm-new' data-bulk-new='1'>+ New watchlist</div>";
  document.body.appendChild(menu);
  var r = anchor.getBoundingClientRect();
  menu.style.top = (r.bottom + window.scrollY + 4) + "px";
  menu.style.left = Math.max(8, Math.min(r.left + window.scrollX, window.scrollX + document.documentElement.clientWidth - (menu.offsetWidth||240) - 8)) + "px";
  function into(key){
    var list = STATE.watchlists.lists[key];
    tickers.forEach(function(t){ if (list.tickers.indexOf(t)===-1) list.tickers.push(t); });
    STATE.watchlists.active = key; saveWatchlists(); closeWatchlistMenu();
    toast("Saved " + tickers.length + " names to <b>" + esc(list.label||key) + "</b>");
  }
  $all("[data-bulk-wl]", menu).forEach(function(el){ el.addEventListener("click", function(){ into(el.dataset.bulkWl); }); });
  menu.querySelector("[data-bulk-new]").addEventListener("click", function(){
    var name = prompt("Name for the new watchlist:"); if (!name) return; name = name.trim(); if (!name) return;
    var key = name.toLowerCase().replace(/[^a-z0-9]+/g,"-").replace(/(^-|-$)/g,"")||uid();
    STATE.watchlists.lists[key] = {label:name, desc:"", tickers:[], indicators: Object.assign({}, DEFAULT_INDICATORS)};
    into(key);
  });
  menu._outside = function(e){ if (!menu.contains(e.target) && e.target!==anchor && !anchor.contains(e.target)) closeWatchlistMenu(); };
  setTimeout(function(){ document.addEventListener("mousedown", menu._outside); }, 0);
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
      "<div class='flex-between'><h2>Backtest</h2>" +
        "<select id='bt-index-select' style='width:auto'>" + activeIndexKeys().map(function(k){ return "<option value='" + esc(k) + "'" + (k===STATE.activeIndex?" selected":"") + ">" + esc(STATE.indexes[k].label||k) + " Index</option>"; }).join("") + "</select></div>" +
      "<p class='muted small'>Composite is the <b>" + esc(getActiveIndex().label||"") + "</b> index (weighted by constituent), vs your selected benchmarks.</p>" +
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
  $("#bt-index-select").addEventListener("change", function(e){ setActiveIndex(e.target.value); showTab("backtest"); });

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

    var datasets = [{ label:"GMR " + (getActiveIndex().label||"") + " Composite", data:composite, borderColor:"#4fd1c5", backgroundColor:"rgba(79,209,197,.1)", fill:true, pointRadius:0, borderWidth:2, tension:.1 }];
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

    var perfCanvas = $("#bt-perf-canvas");
    if (!perfCanvas) return; // user navigated away before data loaded
    if (BT_CHARTS.perf) BT_CHARTS.perf.destroy();
    BT_CHARTS.perf = new Chart(perfCanvas.getContext("2d"), {
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
  if (!root) return; // navigated away before async data resolved
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
    "<div id='pf-form-wrap'></div>" +
    "<div class='card'>" +
      "<h3>Privacy &amp; your data</h3>" +
      "<p class='muted small'>Everything you enter (watchlists, profile, email/phone, GitHub connection) is stored <b>only in this browser</b> &mdash; nothing is sent to any server we run, and it is never shared with other visitors (each browser is separate). Your <b>GitHub token is kept in session storage</b> and is cleared automatically when you close this tab, so it is not left behind. On a <b>shared computer</b>, click below to wipe everything now.</p>" +
      "<div class='cta-row'><button class='btn secondary' id='pf-clear-data'>Clear all my data from this browser</button><span id='pf-clear-msg' class='footer-note'></span></div>" +
    "</div>";

  $("#nl-run").addEventListener("click", runNLCommand);
  $("#nl-input").addEventListener("keydown", function(e){ if (e.key==="Enter") runNLCommand(); });
  $("#pf-clear-data").addEventListener("click", function(){
    if (!confirm("Wipe all Growth Markets Research data (watchlists, indexes, profile, email/phone, GitHub token) from THIS browser? This cannot be undone.")) return;
    clearAllData();
    $("#pf-clear-msg").textContent = "Cleared. Reloading...";
    setTimeout(function(){ location.reload(); }, 600);
  });
  renderProfileForm();
};

function clearAllData(){
  try{
    Object.keys(localStorage).forEach(function(k){ if (k.indexOf(LS_PREFIX)===0) localStorage.removeItem(k); });
    Object.keys(sessionStorage).forEach(function(k){ if (k.indexOf(LS_PREFIX)===0) sessionStorage.removeItem(k); });
  }catch(e){}
}

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
  // Fetch the current sha then PUT; if GitHub reports a 409/422 conflict (the
  // file moved since we read it -- the refresh workflows commit frequently),
  // re-read the latest sha and retry.
  function attempt(triesLeft){
    return ghGet(apiPath).then(function(existing){
      var sha = (existing.ok && existing.json && existing.json.sha) ? existing.json.sha : undefined;
      var body = { message: message, content: b64 };
      if (sha) body.sha = sha;
      return fetch("https://api.github.com" + apiPath, {
        method: "PUT", headers: Object.assign({"Content-Type":"application/json"}, ghHeaders()), body: JSON.stringify(body)
      }).then(function(res){ return res.json().then(function(json){ return {ok:res.ok, status:res.status, json:json}; }); })
        .then(function(r){
          if (!r.ok && (r.status===409 || r.status===422) && triesLeft>0){
            return new Promise(function(res){ setTimeout(res, 400); }).then(function(){ return attempt(triesLeft-1); });
          }
          return r;
        });
    });
  }
  return attempt(3);
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
      "<p class='muted small'>Pick whichever you like &mdash; you can skip email entirely. The recommended no-personal-email options are <b>ntfy</b> (free phone push, no account) and <b>Discord</b>. Configure those as repo secrets (see below); email/SMS are optional and set here.</p>" +
      "<div class='card' style='background:var(--bg2)'>" +
        "<h3 style='margin-top:0'>Recommended: no personal email</h3>" +
        "<div class='grid cols-2'>" +
          "<div><b>ntfy push (free, no signup)</b><p class='small muted' style='margin:4px 0'>Install the <b>ntfy</b> app, subscribe to a private topic, add a repo secret <b>NTFY_TOPIC</b> = that topic. Pushes hit your lock screen &mdash; no need to open the app (enable notifications + Android &#39;instant delivery&#39;).<br><b>Want email too?</b> Make a free ntfy.sh account &rarr; generate an access token &rarr; add secrets <b>NTFY_TOKEN</b> = token and <b>NTFY_EMAIL</b> = your email(s, comma-separated). ntfy forwards each alert to your inbox &mdash; no Gmail needed.</p></div>" +
          "<div><b>Discord webhook (free)</b><p class='small muted' style='margin:4px 0'>In a Discord server: Channel &rarr; Edit &rarr; Integrations &rarr; New Webhook &rarr; Copy URL. Add a repo secret <b>DISCORD_WEBHOOK</b> = that URL. Alerts post to the channel.</p></div>" +
        "</div>" +
      "</div>" +
      "<div class='section-title'>Optional: email &amp; text</div>" +
      "<div class='grid cols-2'>" +
        "<div><label>Email (recipient)</label><input id='chan-email' type='email' value='" + esc((a.channels&&a.channels.email)||"") + "'></div>" +
        "<div><label>Phone number (10 digits)</label><input id='chan-phone' type='password' autocomplete='off' value='" + esc((a.channels&&a.channels.sms&&a.channels.sms.number)||"") + "'></div>" +
        "<div><label>Carrier (SMS via email gateway)</label><select id='chan-carrier'>" +
          Object.keys(SMS_CARRIERS).map(function(k){ return "<option value='" + k + "'" + ((a.channels&&a.channels.sms&&a.channels.sms.carrier)===k?" selected":"") + ">" + SMS_CARRIERS[k] + "</option>"; }).join("") +
        "</select></div>" +
      "</div>" +
      "<p class='footer-note'>Email needs a Gmail App Password secret (GMAIL_APP_PASSWORD; set GMAIL_USER to send from a dedicated Gmail to any address). Email-to-SMS gateways are carrier-dependent and can silently drop messages -- best-effort only; ntfy/Discord are more reliable and free.</p>" +
      "<div class='cta-row'><button class='btn secondary' id='chan-save'>Save channels</button><span id='chan-saved' class='footer-note'></span></div>" +
    "</div>" +
    "<div class='card'>" +
      "<h3>Connect GitHub</h3>" +
      "<p class='muted small'>Needed to push alerts.json / watchlists.json and to dispatch the test workflow. Create a token at " +
        "<a href='https://github.com/settings/tokens/new?scopes=repo,workflow&description=GMR' target='_blank' rel='noopener'>github.com/settings/tokens/new</a> with <b>repo</b> and <b>workflow</b> scopes. " +
        "Your token is stored in this browser&#39;s session only and is cleared when you close the tab.</p>" +
      "<div class='grid cols-2'>" +
        "<div><label>owner/repo</label><input id='gh-repo' type='text' placeholder='yourname/GMR' value='" + esc(STATE.githubRepo||"") + "'></div>" +
        "<div><label>Personal Access Token</label><input id='gh-token' type='password' autocomplete='off' placeholder='ghp_...' value='" + esc(STATE.githubToken||"") + "'></div>" +
      "</div>" +
      "<div class='cta-row'><button class='btn secondary' id='gh-save'>Save connection</button><button class='btn' id='arm-btn'>Arm my alerts</button><span id='arm-status' class='footer-note'></span></div>" +
    "</div>" +
    "<div class='card'>" +
      "<h3>Verify Notifications Work</h3>" +
      "<div class='cta-row'>" +
        "<button class='btn' id='test-alert-btn'>Send me a test alert NOW</button>" +
        "<button class='btn secondary' id='diagnose-btn'>Diagnose setup</button>" +
      "</div>" +
      "<div id='test-status' class='footer-note' style='margin-top:8px'></div>" +
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
    ssSet("githubToken", STATE.githubToken);
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

// Turn a failed GitHub API result into a specific, actionable message.
function ghErrorText(results){
  var fail = results.filter(function(r){ return !r.ok; })[0];
  if (!fail) return "";
  var msg = (fail.json && fail.json.message) || "";
  var s = fail.status;
  if (s === 401) return "401 Bad credentials -- the token is wrong or expired. Generate a new one.";
  if (s === 403) return "403 Forbidden -- the token lacks permission. Use a CLASSIC token with the 'repo' and 'workflow' scopes checked (fine-grained tokens need Contents: read/write AND Workflows: read/write on THIS repo). (" + esc(msg) + ")";
  if (s === 404) return "404 Not Found -- check the repo name is exactly 'owner/repo' (yours is '" + esc(ghRepoPath()) + "'), it exists, and the token can see it.";
  if (s === 409) return "409 Conflict -- the file changed on GitHub since load. Reload the page and try again.";
  if (s === 422) return "422 -- " + esc(msg) + " (often a branch/sha issue; make sure the repo has a 'main' branch).";
  return (s || "error") + " -- " + esc(msg || "unknown");
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
    if (allOk){ status.textContent = "Armed! Your rules will run on the next scheduled workflow tick."; }
    else {
      var err = ghErrorText(results);
      console.error("GMR: arm alerts failed", results);
      status.innerHTML = "<span class='down'>Failed &mdash; " + err + "</span>";
    }
  }).catch(function(e){
    console.error("GMR: arm alerts failed", e);
    status.textContent = "Push failed -- see console for details.";
  });
}

function sendTestAlert(){
  if (!requireGithubConnection()) return;
  var btn = $("#test-alert-btn");
  var status = $("#test-status");
  var repo = ghRepoPath();
  var runsUrl = "https://github.com/" + repo + "/actions/workflows/nri-email.yml";
  btn.disabled = true; btn.textContent = "Sending...";
  status.innerHTML = "Dispatching test alert...";
  var startedAt = Date.now();
  ghDispatchWorkflow("nri-email.yml", { test: "true" }).then(function(res){
    if (!res.ok){
      btn.disabled = false; btn.textContent = "Send me a test alert NOW";
      status.innerHTML = "<span class='down'>Dispatch failed (" + res.status + "). Make sure the workflow file is pushed (Methodology tab) and your token has the <b>workflow</b> scope.</span>";
      return;
    }
    status.innerHTML = "Dispatched. Waiting for the run to finish (~30-60s)...";
    // poll the latest run for this workflow
    var tries = 0;
    (function poll(){
      tries++;
      ghGet("/repos/" + repo + "/actions/workflows/nri-email.yml/runs?per_page=1").then(function(r){
        var run = r.json && r.json.workflow_runs && r.json.workflow_runs[0];
        var fresh = run && (new Date(run.created_at).getTime() > startedAt - 20000);
        if (fresh && run.status === "completed"){
          btn.disabled = false; btn.textContent = "Send me a test alert NOW";
          if (run.conclusion === "success"){
            status.innerHTML = "<span class='up'>Run succeeded.</span> If nothing arrived, no delivery channel is set &mdash; add an <b>NTFY_TOPIC</b> (free push), <b>DISCORD_WEBHOOK</b>, or <b>GMAIL_APP_PASSWORD</b> secret, then retry. <a href='" + run.html_url + "' target='_blank' rel='noopener'>View run log</a> (it prints exactly what was sent or why not).";
          } else {
            status.innerHTML = "<span class='down'>Run " + esc(run.conclusion||"failed") + ".</span> <a href='" + run.html_url + "' target='_blank' rel='noopener'>Open the run log</a> to see the error.";
          }
          return;
        }
        if (tries < 20){ setTimeout(poll, 5000); }
        else {
          btn.disabled = false; btn.textContent = "Send me a test alert NOW";
          status.innerHTML = "Still running. <a href='" + runsUrl + "' target='_blank' rel='noopener'>Check the Actions tab</a> for the result &amp; log.";
        }
      }).catch(function(){ if (tries < 20) setTimeout(poll, 5000); });
    })();
  }).catch(function(e){
    btn.disabled = false; btn.textContent = "Send me a test alert NOW";
    console.error("GMR: test dispatch failed", e);
    status.innerHTML = "<span class='down'>Dispatch failed -- see console.</span>";
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
    {label:"NTFY_TOPIC secret (free push)", path:"/repos/" + repo + "/actions/secrets/NTFY_TOPIC", optional:true},
    {label:"DISCORD_WEBHOOK secret", path:"/repos/" + repo + "/actions/secrets/DISCORD_WEBHOOK", optional:true},
    {label:"GMAIL_APP_PASSWORD secret", path:"/repos/" + repo + "/actions/secrets/GMAIL_APP_PASSWORD", optional:true},
    {label:"Last workflow run status", path:"/repos/" + repo + "/actions/workflows/nri-email.yml/runs?per_page=1"}
  ];
  Promise.all(checks.map(function(c){ return ghGet(c.path).then(function(r){ return {label:c.label, ok:r.ok, json:r.json, optional:c.optional}; }); }))
    .then(function(results){
      var anyChannel = false;
      var rows = results.map(function(r){
        var detail = "";
        if (r.label === "Last workflow run status"){
          var run = r.json && r.json.workflow_runs && r.json.workflow_runs[0];
          detail = run ? (run.status + "/" + (run.conclusion||"pending")) : "no runs yet";
          r.ok = !!run;
        }
        if (r.optional && r.ok) anyChannel = true;
        var cls = r.ok ? "diag-ok" : (r.optional ? "muted" : "diag-bad");
        var txt = r.ok ? "OK" : (r.optional ? "not set" : "MISSING");
        return "<tr><td>" + esc(r.label) + "</td><td class='" + cls + "'>" + txt + (detail?" (" + esc(detail) + ")":"") + "</td></tr>";
      });
      rows.push("<tr><td><b>At least one delivery channel set</b></td><td class='" + (anyChannel?"diag-ok":"diag-bad") + "'>" + (anyChannel?"OK":"ADD ntfy / Discord / Gmail secret") + "</td></tr>");
      root.innerHTML = "<table class='status-table'><tbody>" + rows.join("") + "</tbody></table>" +
        "<p class='footer-note'>You only need ONE channel. ntfy (NTFY_TOPIC) is the easiest &mdash; free push, no personal email.</p>";
    })
    .catch(function(e){
      console.error("GMR: diagnose failed", e);
      root.innerHTML = "<p class='muted small'>Diagnostics failed -- check your token/repo and console.</p>";
    });
}
"""

JS_METHODOLOGY = r"""
// ---- Methodology tab ----------------------------------------------------
var METH_MODE = null;
var CADENCE_OPTIONS = ["daily","weekly","monthly","quarterly","yearly","off"];

RENDERERS.methodology = function(root){
  var wlKeys = activeWatchlistKeys();
  if (!METH_MODE) METH_MODE = "idx:" + STATE.activeIndex;
  root.innerHTML =
    "<div class='card'>" +
      "<h2>Methodology</h2>" +
      "<label>Show methodology for</label>" +
      "<select id='meth-select'>" +
        "<optgroup label='Indexes'>" +
          activeIndexKeys().map(function(k){ return "<option value='idx:" + esc(k) + "'" + (METH_MODE==="idx:"+k?" selected":"") + ">" + esc(STATE.indexes[k].label||k) + " Index</option>"; }).join("") +
        "</optgroup>" +
        (wlKeys.length ? "<optgroup label='Watchlists'>" + wlKeys.map(function(k){ return "<option value='wl:" + esc(k) + "'" + (METH_MODE==="wl:"+k?" selected":"") + ">Watchlist: " + esc(STATE.watchlists.lists[k].label||k) + "</option>"; }).join("") + "</optgroup>" : "") +
      "</select>" +
    "</div>" +
    "<div id='meth-body'></div>";

  $("#meth-select").addEventListener("change", function(e){ METH_MODE = e.target.value; renderMethodologyBody(); });
  renderMethodologyBody();
};

function renderMethodologyBody(){
  var root = $("#meth-body");
  if (METH_MODE.indexOf("idx:") === 0){
    var ikey = METH_MODE.slice(4);
    if (STATE.indexes[ikey] && STATE.activeIndex !== ikey) setActiveIndex(ikey); // edits apply to the selected index
    renderFeaturedMethodology(root);
    return;
  }
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
      "<h3>" + esc(getActiveIndex().label||"Index") + " &mdash; Tiered Weights</h3>" +
      "<p class='muted small'>Total allocated weight: " + fmtNum(totalWeight,1) + "% (should sum to 100%). Tier 1 names are core holdings; Tier 2 are satellite/emerging exposure. Edits here update this index everywhere.</p>" +
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
      "<div><label>GitHub Personal Access Token (repo + workflow scopes)</label><input id='meth-token' type='password' autocomplete='off' placeholder='ghp_...' value='" + esc(STATE.githubToken||"") + "'></div>" +
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
    ssSet("githubToken", STATE.githubToken);

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
      if (allOk){ status.textContent = "Scheduled emails are on. Add a delivery secret (NTFY_TOPIC / DISCORD_WEBHOOK / GMAIL_APP_PASSWORD) in repo settings, then use Alerts -> Send a test alert."; }
      else {
        console.error("GMR: turn on scheduled emails failed", results);
        status.innerHTML = "<span class='down'>Failed &mdash; " + ghErrorText(results) + "</span>";
      }
    }).catch(function(e){
      console.error("GMR: turn on scheduled emails failed", e);
      status.textContent = "Push failed -- see console for details.";
    });
  });
}
"""

JS_INDEXES = r"""
// ---- Indexes tab: create + track weighted baskets for any vertical --------
RENDERERS.indexes = function(root){
  var keys = Object.keys(STATE.indexes);
  root.innerHTML =
    "<div class='card'>" +
      "<div class='flex-between'><div><h2>Indexes</h2>" +
        "<p class='muted small'>Build weighted baskets for any vertical market and track them like the featured Nuclear index -- composite chart, sector mix, and backtest.</p></div></div>" +
      "<div class='section-title'>Create a new index</div>" +
      "<div class='grid cols-4'>" +
        "<div><label>Name</label><input id='idx-name' type='text' placeholder='e.g. My Semis Index'></div>" +
        "<div><label>Source</label><select id='idx-source'>" +
          "<optgroup label='Your watchlists'>" + activeWatchlistKeys().map(function(k){ return "<option value='wl:" + esc(k) + "'>" + esc(STATE.watchlists.lists[k].label||k) + "</option>"; }).join("") + "</optgroup>" +
          "<optgroup label='Sector presets'>" + STATE.presets.map(function(p){ return "<option value='ps:" + esc(p.key) + "'>" + esc(p.label) + "</option>"; }).join("") + "</optgroup>" +
        "</select></div>" +
        "<div><label>Weighting</label><select id='idx-method'><option value='market-cap'>Market cap</option><option value='equal'>Equal weight</option></select></div>" +
        "<div style='display:flex;align-items:flex-end'><button class='btn' id='idx-create'>Create index</button></div>" +
      "</div>" +
    "</div>" +
    "<div id='idx-list' class='grid cols-2'></div>";

  $("#idx-create").addEventListener("click", createIndexFromForm);
  renderIndexCards();
};

function createIndexFromForm(){
  var name = ($("#idx-name").value||"").trim();
  var source = $("#idx-source").value;
  var method = $("#idx-method").value;
  if (!name){ alert("Give the index a name."); return; }
  if (!source){ alert("Pick a source watchlist or preset."); return; }
  var tickers = [];
  if (source.indexOf("wl:")===0){ var l = STATE.watchlists.lists[source.slice(3)]; tickers = l ? l.tickers.slice() : []; }
  else if (source.indexOf("ps:")===0){ var p = STATE.presets.filter(function(x){return x.key===source.slice(3);})[0]; tickers = p ? p.tickers.slice() : []; }
  if (tickers.length < 2){ alert("Need at least 2 tickers."); return; }

  var btn = $("#idx-create"); btn.disabled = true; btn.textContent = "Building...";
  // market-cap weighting needs baked fundamentals; fetch series (which carry
  // fundamentals for baked tickers) then build.
  Promise.all(tickers.map(function(t){ return getSeries(t).then(function(s){ return {t:t, cap:(s.fundamentals&&s.fundamentals.marketCap)||0}; }); })).then(function(rows){
    var capBy = {}; rows.forEach(function(r){ capBy[r.t] = r.cap; });
    if (method === "market-cap" && rows.every(function(r){ return !r.cap; })) method = "equal";
    var key = createIndexFromTickers(name, tickers, method, capBy);
    // enrich constituent names/sectors from fundamentals where available
    Promise.all(tickers.map(function(t){ return getSeries(t); })).then(function(seriesList){
      seriesList.forEach(function(s, i){
        var f = s.fundamentals || {};
        var c = STATE.indexes[key].constituents[i];
        if (c){ if (f.name) c.name = f.name; if (f.sector) c.sector = f.sector; }
      });
      saveIndexes();
      setActiveIndex(key);
      toast("Created &amp; activated <b>" + esc(name) + "</b>");
      showTab("indexes");
    });
  }).catch(function(e){ console.error("GMR: create index failed", e); btn.disabled=false; btn.textContent="Create index"; });
}

function renderIndexCards(){
  var root = $("#idx-list");
  var keys = activeIndexKeys();
  var archivedKeys = Object.keys(STATE.indexes).filter(function(k){ return STATE.indexes[k].archived; });
  root.innerHTML = keys.map(function(k){
    var idx = STATE.indexes[k];
    var active = k === STATE.activeIndex;
    return "<div class='card'>" +
      "<div class='flex-between'><div><h3 style='margin:0;color:var(--text);text-transform:none;font-size:16px'>" + esc(idx.label||k) + (active?" <span class='pill up'>active</span>":"") + "</h3>" +
        "<p class='muted small'>" + (idx.constituents||[]).length + " constituents</p></div></div>" +
      "<div class='chart-wrap small'><canvas id='idxc-" + esc(k) + "'></canvas></div>" +
      "<div class='cta-row'>" +
        (active ? "" : "<button class='btn small' data-idx-activate='" + esc(k) + "'>Make active</button>") +
        "<button class='btn small secondary' data-idx-backtest='" + esc(k) + "'>Backtest</button>" +
        "<button class='btn small ghost' data-idx-heatmap='" + esc(k) + "'>Heatmap</button>" +
        (k==="nuclear" ? "" : "<button class='btn small ghost' data-idx-archive='" + esc(k) + "'>Archive</button>") +
        (k==="nuclear" ? "" : "<button class='btn small ghost' data-idx-delete='" + esc(k) + "'>Delete</button>") +
      "</div></div>";
  }).join("") +
  (archivedKeys.length ? "<div class='card' style='grid-column:1/-1'><details class='archived-block'><summary>Archived indexes (" + archivedKeys.length + ")</summary><div class='row' style='margin-top:8px'>" +
    archivedKeys.map(function(k){ return "<span class='chip muted'>" + esc(STATE.indexes[k].label||k) + " <button class='btn small ghost' data-idx-restore='" + esc(k) + "'>Restore</button><button class='btn small ghost' data-idx-del2='" + esc(k) + "'>Delete</button></span>"; }).join("") +
    "</div></details></div>" : "");

  keys.forEach(function(k){ renderCompositeMini($("#idxc-" + k), STATE.indexes[k].constituents); });
  $all("[data-idx-activate]", root).forEach(function(b){ b.addEventListener("click", function(){ setActiveIndex(b.dataset.idxActivate); toast("Active index: <b>" + esc(STATE.indexes[b.dataset.idxActivate].label) + "</b>"); showTab("indexes"); }); });
  $all("[data-idx-backtest]", root).forEach(function(b){ b.addEventListener("click", function(){ setActiveIndex(b.dataset.idxBacktest); showTab("backtest"); }); });
  $all("[data-idx-heatmap]", root).forEach(function(b){ b.addEventListener("click", function(){ lsSet("heatmapSource", "idx:" + b.dataset.idxHeatmap); showTab("heatmap"); }); });
  $all("[data-idx-archive]", root).forEach(function(b){ b.addEventListener("click", function(){ archiveIndex(b.dataset.idxArchive); toast("Archived index"); showTab("indexes"); }); });
  $all("[data-idx-delete]", root).forEach(function(b){ b.addEventListener("click", function(){ if(confirm("Delete this index?")){ deleteIndex(b.dataset.idxDelete); showTab("indexes"); } }); });
  $all("[data-idx-restore]", root).forEach(function(b){ b.addEventListener("click", function(){ STATE.indexes[b.dataset.idxRestore].archived=false; saveIndexes(); showTab("indexes"); }); });
  $all("[data-idx-del2]", root).forEach(function(b){ b.addEventListener("click", function(){ if(confirm("Permanently delete this index?")){ deleteIndex(b.dataset.idxDel2); showTab("indexes"); } }); });
}

function renderCompositeMini(canvas, cons){
  if (!canvas || !cons || !cons.length) return;
  var tickers = cons.map(function(c){ return c.ticker; });
  Promise.all(tickers.map(function(t){ return getSeries(t); })).then(function(seriesList){
    var baseDates = seriesList.reduce(function(a,s){ return s.dates.length>a.length?s.dates:a; }, []);
    var totalW = cons.reduce(function(a,c){ return a+(c.weight||0); }, 0) || 1;
    var composite = baseDates.map(function(d, i){
      var sum=0, wsum=0;
      seriesList.forEach(function(s, idx){
        var off = baseDates.length - s.closes.length; var si = i - off;
        if (si<0 || !s.closes[0]) return;
        sum += (s.closes[si]/s.closes[0])*100 * (cons[idx].weight||0); wsum += (cons[idx].weight||0);
      });
      return wsum ? sum/wsum : null;
    });
    var last = composite.filter(function(v){return v!=null;});
    var up = last.length>1 && last[last.length-1] >= last[0];
    new Chart(canvas.getContext("2d"), {
      type:"line", data:{ labels:baseDates, datasets:[{ data:composite, borderColor: up?"#3ecf8e":"#f56565", backgroundColor:"transparent", pointRadius:0, borderWidth:1.6, tension:.15 }] },
      options:{ maintainAspectRatio:false, plugins:{legend:{display:false}, tooltip:{enabled:false}}, scales:{ x:{display:false}, y:{ position:"right", ticks:{color:"#93a2bb", maxTicksLimit:3}, grid:{color:"#1b2536"} } } }
    });
  }).catch(function(e){ console.error("GMR: composite mini failed", e); });
}
"""

JS_HEATMAP = r"""
// ---- Heatmap tab: Finviz-style tiles, filterable by any basket ------------
var HM_PERIODS = [["1D",1],["1W",5],["1M",21],["3M",63],["YTD",-1],["1Y",252]];
var HM_SIZE = [["cap","Size by market cap"],["equal","Equal size"]];

function heatSources(){
  var out = [];
  activeIndexKeys().forEach(function(k){ out.push({id:"idx:"+k, label:"Index: "+(STATE.indexes[k].label||k), tickers:(STATE.indexes[k].constituents||[]).map(function(c){return c.ticker;})}); });
  activeWatchlistKeys().forEach(function(k){ out.push({id:"wl:"+k, label:"Watchlist: "+(STATE.watchlists.lists[k].label||k), tickers:(STATE.watchlists.lists[k].tickers||[]).slice()}); });
  STATE.presets.forEach(function(p){ out.push({id:"ps:"+p.key, label:"Vertical: "+p.label, tickers:p.tickers.slice()}); });
  return out;
}

RENDERERS.heatmap = function(root){
  var sources = heatSources();
  var sel = lsGet("heatmapSource", "idx:" + STATE.activeIndex);
  if (!sources.some(function(s){ return s.id===sel; })) sel = sources[0] ? sources[0].id : "";
  var period = lsGet("heatmapPeriod", "1D");
  var sizeMode = lsGet("heatmapSize", "cap");

  root.innerHTML =
    "<div class='card'>" +
      "<div class='flex-between'><div><h2>Heatmap</h2>" +
        "<p class='muted small'>Performance heatmap across any basket -- green up, red down, tiles sized by market cap and grouped by sector. Click a tile to open it.</p></div></div>" +
      "<div class='row'>" +
        "<div><label>Source</label><select id='hm-source'>" + sources.map(function(s){ return "<option value='" + esc(s.id) + "'" + (s.id===sel?" selected":"") + ">" + esc(s.label) + "</option>"; }).join("") + "</select></div>" +
        "<div><label>Period</label><select id='hm-period'>" + HM_PERIODS.map(function(p){ return "<option value='" + p[0] + "'" + (p[0]===period?" selected":"") + ">" + p[0] + "</option>"; }).join("") + "</select></div>" +
        "<div><label>Sizing</label><select id='hm-size'>" + HM_SIZE.map(function(m){ return "<option value='" + m[0] + "'" + (m[0]===sizeMode?" selected":"") + ">" + m[1] + "</option>"; }).join("") + "</select></div>" +
      "</div>" +
    "</div>" +
    "<div id='hm-grid'><p class='muted small'>Loading heatmap...</p></div>";

  $("#hm-source").addEventListener("change", function(e){ lsSet("heatmapSource", e.target.value); showTab("heatmap"); });
  $("#hm-period").addEventListener("change", function(e){ lsSet("heatmapPeriod", e.target.value); showTab("heatmap"); });
  $("#hm-size").addEventListener("change", function(e){ lsSet("heatmapSize", e.target.value); showTab("heatmap"); });

  var src = sources.filter(function(s){ return s.id===sel; })[0];
  if (!src || !src.tickers.length){ $("#hm-grid").innerHTML = "<div class='card'><p class='muted small'>This basket has no tickers.</p></div>"; return; }
  renderHeatmapGrid(src.tickers, period, sizeMode);
};

function periodChange(s, period){
  var closes = s.closes; if (!closes || closes.length<2) return 0;
  var last = closes[closes.length-1];
  if (period === "YTD"){
    var yr = new Date().getFullYear();
    var idx = s.dates.findIndex(function(d){ return d >= (yr + "-01-01"); });
    if (idx > 0) return (last/closes[idx]-1)*100;
    return (last/closes[0]-1)*100;
  }
  var n = 1; HM_PERIODS.forEach(function(p){ if(p[0]===period) n=p[1]; });
  var ref = closes.length>n ? closes[closes.length-1-n] : closes[0];
  return (last/ref-1)*100;
}
function heatBg(pct){
  var m = Math.max(0, Math.min(1, Math.abs(pct)/6));
  var a = 0.18 + m*0.72;
  return pct>=0 ? "rgba(34,197,94," + a.toFixed(2) + ")" : "rgba(239,68,68," + a.toFixed(2) + ")";
}
function capBucket(cap){
  if (cap >= 5e11) return "xl";
  if (cap >= 1e11) return "lg";
  if (cap >= 2e10) return "md";
  return "sm";
}

function renderHeatmapGrid(tickers, period, sizeMode){
  var root = $("#hm-grid");
  Promise.all(tickers.map(function(t){ return getSeries(t).then(function(s){ return {t:t, s:s}; }); })).then(function(rows){
    var bySector = {};
    rows.forEach(function(r){
      var f = r.s.fundamentals || {};
      var sector = f.sector || "Other";
      var cap = f.marketCap || 0;
      var chg = periodChange(r.s, period);
      (bySector[sector] = bySector[sector] || []).push({ ticker:r.t, chg:chg, cap:cap, name:f.name||r.t });
    });
    var sectors = Object.keys(bySector).sort(function(a,b){
      var ca = bySector[a].reduce(function(x,y){return x+y.cap;},0), cb = bySector[b].reduce(function(x,y){return x+y.cap;},0);
      return cb - ca;
    });
    var html = sectors.map(function(sec){
      var items = bySector[sec].sort(function(a,b){ return b.cap - a.cap; });
      var tiles = items.map(function(it){
        var sizeCls = sizeMode==="cap" ? capBucket(it.cap) : "md";
        return "<div class='heat-tile " + sizeCls + "' data-heat='" + esc(it.ticker) + "' style='background:" + heatBg(it.chg) + "' title='" + esc(it.name) + (it.cap?" -- " + fmtBig(it.cap):"") + "'>" +
          "<div class='ht-sym'>" + esc(it.ticker) + "</div>" +
          "<div class='ht-chg'>" + fmtPct(it.chg) + "</div></div>";
      }).join("");
      return "<div class='heat-sector'><div class='heat-sector-head'>" + esc(sec) + "</div><div class='heat-tiles'>" + tiles + "</div></div>";
    }).join("");
    root.innerHTML = html + "<p class='footer-note'>Change over " + esc(period) + ". Market-cap sizing uses baked fundamentals; tickers without them show a default size.</p>";
    $all("[data-heat]", root).forEach(function(el){ el.addEventListener("click", function(){ CO_TICKER = el.dataset.heat; lsSet("companiesTicker", CO_TICKER); showTab("companies"); }); });
  }).catch(function(e){ console.error("GMR: heatmap failed", e); root.innerHTML = "<div class='card'><p class='muted small'>Could not build the heatmap right now.</p></div>"; });
}
"""

JS_KG = r"""
// ---- Money Flow: financial knowledge graph (SEC-sourced) ------------------
var KG_OUT_META = [
  ["cogs","Cost of Revenue","#f56565"],
  ["rnd","R&D","#f6ad55"],
  ["sga","SG&A","#f6ad55"],
  ["interest","Interest","#f56565"],
  ["taxes","Taxes","#f56565"],
  ["net","Net Income","#3ecf8e"],
  ["capex","Capex","#5b8cff"],
  ["dividends","Dividends","#a78bfa"],
  ["buybacks","Buybacks","#a78bfa"]
];

var KG_AGG_SECTOR = null; // drill-down sector filter for the aggregate view
function kgSources(){
  var out = heatSources();
  // macro option: the entire tracked market (all baked SEC filers)
  var allSec = (window.GMR_SEC_INDEX && window.GMR_SEC_INDEX.tickers) || [];
  out.unshift({ id:"all:market", label:"Entire tracked market", tickers: allSec });
  return out;
}

RENDERERS.moneyflow = function(root){
  var mode = lsGet("kgMode", "relationships");
  var relScope = lsGet("kgRelScope", "company");
  var ticker = lsGet("kgTicker", CO_TICKER || "NVDA");
  var sources = kgSources();
  var basket = lsGet("kgBasket", "idx:" + STATE.activeIndex);
  if (!sources.some(function(s){ return s.id===basket; })) basket = sources[0] ? sources[0].id : "";

  root.innerHTML =
    "<div class='card'>" +
      "<div class='flex-between'><div><h2>Money Flow &mdash; Financial Knowledge Graph</h2>" +
        "<p class='muted small'><b>Relationships</b>: a web of how companies connect &mdash; who supplies whom (vertical / supply-chain), who competes (horizontal), B2B customers, licensing, partnerships, and M&amp;A &mdash; click any node to traverse it. " +
        "<b>Company spend</b> &amp; <b>Aggregate</b>: where money goes, from one SEC filing up to a whole vertical or the entire market.</p>" +
        "<details class='kg-sources'><summary>Sources &amp; methodology</summary>" +
          "<ul class='small muted' style='margin:6px 0 0;padding-left:18px;line-height:1.6'>" +
            "<li><b>Revenue &amp; spending (Company spend / Aggregate):</b> U.S. SEC EDGAR <b>XBRL company-facts API</b> (data.sec.gov) &mdash; the exact figures companies report in their latest annual 10-K / 20-F / 40-F filings. Latest fiscal-year value per concept.</li>" +
            "<li><b>Relationships (supply-chain / competitor / customer / licensing / partner / M&amp;A):</b> hand-curated from SEC filings (10-K customer &amp; segment disclosures), company investor presentations &amp; press releases, and reputable public reporting; date-stamped as of " + esc((STATE.relationships.updated)||"the build") + ". Illustrative, not exhaustive, not investment advice.</li>" +
            "<li><b>Money-flow status on nodes (accumulating / distributing):</b> Chaikin Money Flow (CMF-21) computed in-app from price &amp; volume.</li>" +
            "<li><b>Prices, market cap, sector/industry:</b> Yahoo Finance (quotes &amp; fundamentals) with Stooq fallback; refreshed on a schedule via GitHub Actions.</li>" +
          "</ul></details></div></div>" +
      "<div class='row'>" +
        "<div class='seg' id='kg-mode'>" +
          "<button data-kg='relationships'" + (mode==="relationships"?" class='on'":"") + ">Relationships</button>" +
          "<button data-kg='company'" + (mode==="company"?" class='on'":"") + ">Company spend</button>" +
          "<button data-kg='aggregate'" + (mode==="aggregate"?" class='on'":"") + ">Aggregate (macro)</button>" +
        "</div>" +
        (mode==="relationships"
          ? "<div class='seg' id='kg-relscope'><button data-scope='company'" + (relScope==="company"?" class='on'":"") + ">Company-centered</button><button data-scope='basket'" + (relScope==="basket"?" class='on'":"") + ">Vertical / index web</button></div>" +
            (relScope==="company"
              ? "<div><label>Center company</label><input id='kg-ticker' type='text' value='" + esc(ticker) + "' style='width:130px;text-transform:uppercase'></div><div style='display:flex;align-items:flex-end'><button class='btn small' id='kg-load'>Show</button></div>"
              : "<div><label>Basket</label><select id='kg-basket'>" + sources.map(function(s){ return "<option value='" + esc(s.id) + "'" + (s.id===basket?" selected":"") + ">" + esc(s.label) + "</option>"; }).join("") + "</select></div>")
          : mode==="aggregate"
            ? "<div><label>Scope</label><select id='kg-basket'>" + sources.map(function(s){ return "<option value='" + esc(s.id) + "'" + (s.id===basket?" selected":"") + ">" + esc(s.label) + "</option>"; }).join("") + "</select></div>"
            : "<div><label>Ticker</label><input id='kg-ticker' type='text' value='" + esc(ticker) + "' style='width:130px;text-transform:uppercase'></div><div style='display:flex;align-items:flex-end'><button class='btn small' id='kg-load'>Show</button></div>") +
      "</div>" +
    "</div>" +
    "<div class='card' id='kg-canvas'><p class='muted small'>Loading...</p></div>";

  $all("#kg-mode button", root).forEach(function(b){ b.addEventListener("click", function(){ lsSet("kgMode", b.getAttribute("data-kg")); KG_AGG_SECTOR=null; showTab("moneyflow"); }); });
  $all("#kg-relscope button", root).forEach(function(b){ b.addEventListener("click", function(){ lsSet("kgRelScope", b.getAttribute("data-scope")); showTab("moneyflow"); }); });

  if (mode==="aggregate"){
    $("#kg-basket").addEventListener("change", function(e){ lsSet("kgBasket", e.target.value); KG_AGG_SECTOR=null; renderAggregateFlow(e.target.value); });
    renderAggregateFlow(basket);
  } else if (mode==="relationships" && relScope==="basket"){
    $("#kg-basket").addEventListener("change", function(e){ lsSet("kgBasket", e.target.value); renderBasketWeb(e.target.value); });
    renderBasketWeb(basket);
  } else {
    var load = function(){ var t=($("#kg-ticker").value||"").trim().toUpperCase(); if(t){ lsSet("kgTicker", t); if(mode==="company") renderCompanyFlow(t); else renderRelationships(t); } };
    $("#kg-load").addEventListener("click", load);
    $("#kg-ticker").addEventListener("keydown", function(e){ if(e.key==="Enter") load(); });
    if (mode==="company") renderCompanyFlow(ticker); else renderRelationships(ticker);
  }
};

// ---- Relationships ego-graph: who a company supplies, buys from, competes
// with, licenses, partners, owns -- plus the edges among those neighbors, so
// you see the local web and can traverse it by clicking any node.
var KG_REL_FILTER = null; // set of enabled types, null = all
function relEdges(){
  var edges = (STATE.relationships.edges || []).slice();
  // auto-derive competitor edges from shared sub-industry within the curated set
  // (kept implicit to avoid clutter; curated competitor edges already exist).
  return edges;
}
function renderRelationships(center){
  center = (center||"").toUpperCase();
  var root = $("#kg-canvas");
  var types = STATE.relationships.types || {};
  var allEdges = relEdges();
  var enabled = KG_REL_FILTER || Object.keys(types);

  // neighbors of center (any direction), then edges among {center}+neighbors
  var neigh = {};
  allEdges.forEach(function(e){
    if (enabled.indexOf(e.type)===-1) return;
    if (e.a===center) neigh[e.b]=1;
    else if (e.b===center) neigh[e.a]=1;
  });
  var nodes = [center].concat(Object.keys(neigh));
  var inSet = {}; nodes.forEach(function(n){ inSet[n]=1; });
  var edges = allEdges.filter(function(e){ return enabled.indexOf(e.type)!==-1 && inSet[e.a] && inSet[e.b]; });

  var legend = "<div class='row' id='kg-rel-filter' style='margin-bottom:6px'>" +
    Object.keys(types).map(function(t){
      var on = enabled.indexOf(t)!==-1;
      return "<span class='chip" + (on?" active":"") + "' data-rel-type='" + esc(t) + "' title='" + esc(types[t].desc) + "'><span class='badge-dot' style='background:" + types[t].color + "'></span>" + esc(types[t].label) + "</span>";
    }).join("") + "</div>";

  if (Object.keys(neigh).length === 0){
    root.innerHTML = legend + "<p class='muted small'>No curated relationships for <b>" + esc(center) + "</b> yet. Try a name with rich supply-chain ties like NVDA, TSM, CEG, LEU, MSFT, LLY, or TSLA. " +
      "(This is a hand-curated map of the tracked universe -- suppliers, customers, competitors, licensing, partnerships, and M&A -- from public filings and reporting.)</p>";
    bindRelFilter(root, center, enabled);
    return;
  }

  // radial layout
  var W = 960, H = Math.max(460, 120 + Object.keys(neigh).length*26), cx=W/2, cy=H/2;
  var R = Math.min(W,H)*0.34;
  var pos = {}; pos[center] = {x:cx, y:cy};
  Object.keys(neigh).forEach(function(n, i){
    var ang = (i/Object.keys(neigh).length)*Math.PI*2 - Math.PI/2;
    pos[n] = {x: cx+Math.cos(ang)*R, y: cy+Math.sin(ang)*R};
  });
  var svg = "<svg viewBox='0 0 " + W + " " + H + "' width='100%' style='max-height:" + H + "px'>" +
    "<defs><marker id='kgarrow' markerWidth='9' markerHeight='9' refX='7' refY='3' orient='auto'><path d='M0,0 L7,3 L0,6 Z' fill='#93a2bb'/></marker></defs>";
  // edges
  edges.forEach(function(e){
    var p1=pos[e.a], p2=pos[e.b]; if(!p1||!p2) return;
    var col = (types[e.type]||{}).color || "#93a2bb";
    var directed = (types[e.type]||{}).directed;
    // shorten to node edges so arrowheads sit outside the circles
    var dx=p2.x-p1.x, dy=p2.y-p1.y, len=Math.sqrt(dx*dx+dy*dy)||1, ux=dx/len, uy=dy/len;
    var x1=p1.x+ux*26, y1=p1.y+uy*26, x2=p2.x-ux*30, y2=p2.y-uy*30;
    svg += "<line x1='" + x1.toFixed(1) + "' y1='" + y1.toFixed(1) + "' x2='" + x2.toFixed(1) + "' y2='" + y2.toFixed(1) + "' stroke='" + col + "' stroke-opacity='.55' stroke-width='2'" + (directed?" marker-end='url(#kgarrow)'":"") + "><title>" + esc(e.a + " -> " + e.b + ": " + ((types[e.type]||{}).label||e.type) + (e.note?(" (" + e.note + ")"):"")) + "</title></line>";
  });
  // nodes
  nodes.forEach(function(n){
    var p=pos[n]; var isC = n===center;
    var rad = isC?34:24;
    svg += "<g class='kg-rnode' data-rel-node='" + esc(n) + "' style='cursor:pointer'>" +
      "<circle cx='" + p.x.toFixed(1) + "' cy='" + p.y.toFixed(1) + "' r='" + rad + "' fill='" + (isC?"rgba(79,209,197,.22)":"var(--panel2)") + "' stroke='" + (isC?"#4fd1c5":"#26324a") + "' stroke-width='" + (isC?2:1.5) + "'/>" +
      "<text x='" + p.x.toFixed(1) + "' y='" + (p.y+4).toFixed(1) + "' text-anchor='middle' fill='#e7edf7' font-size='" + (isC?13:12) + "' font-weight='700'>" + esc(n) + "</text></g>";
  });
  svg += "</svg>";

  // relationship list (the who/what)
  var listRows = edges.map(function(e){
    var t = types[e.type]||{};
    var arrow = t.directed ? " &rarr; " : " &harr; ";
    return "<tr><td><b>" + esc(e.a) + "</b>" + arrow + "<b>" + esc(e.b) + "</b></td>" +
      "<td><span class='badge-dot' style='background:" + (t.color||"#93a2bb") + "'></span>" + esc(t.label||e.type) + "</td>" +
      "<td class='muted'>" + esc(e.note||"") + "</td></tr>";
  }).join("");

  root.innerHTML = legend +
    "<div class='flex-between'><h3 style='margin:2px 0'>" + esc(center) + " &mdash; relationship web (" + Object.keys(neigh).length + " connections)</h3>" +
      "<button class='btn small ghost' id='kg-open-co'>Open " + esc(center) + " &rarr;</button></div>" +
    "<p class='muted small' style='margin:0 0 6px'>Click any node to re-center the graph on it and traverse the web. Arrows point supplier&rarr;customer / acquirer&rarr;target / licensor&rarr;licensee.</p>" +
    "<div style='overflow-x:auto'>" + svg + "</div>" +
    "<table style='margin-top:10px'><thead><tr><th>Relationship</th><th>Type</th><th>Detail</th></tr></thead><tbody>" + listRows + "</tbody></table>" +
    "<p class='footer-note'>Hand-curated from public filings, earnings materials, and widely reported news for the tracked universe -- illustrative, not exhaustive, not investment advice. " +
      "Vertical (supply-chain) ties reveal integration/acquisition targets; horizontal ties reveal competitors and consolidation; customer/partner ties reveal B2B demand.</p>";

  $all("[data-rel-node]", root).forEach(function(el){ el.addEventListener("click", function(){ var t=el.getAttribute("data-rel-node"); lsSet("kgTicker", t); renderRelationships(t); }); });
  var ob = $("#kg-open-co"); if (ob) ob.addEventListener("click", function(){ CO_TICKER = center; lsSet("companiesTicker", center); showTab("companies"); });
  bindRelFilter(root, center, enabled);
}
function bindRelFilter(root, center, enabled){
  $all("[data-rel-type]", root).forEach(function(chip){
    chip.addEventListener("click", function(){
      var t = chip.dataset.relType;
      var set = enabled.slice();
      var i = set.indexOf(t);
      if (i===-1) set.push(t); else set.splice(i,1);
      KG_REL_FILTER = set.length ? set : Object.keys(STATE.relationships.types);
      renderRelationships(center);
    });
  });
}

// ---- Basket web: force-directed graph of ALL curated ties among a whole
// watchlist / vertical / index, to reveal cluster-wide dependencies (e.g.,
// how much of a basket funnels through one supplier).
function renderBasketWeb(sourceId){
  var root = $("#kg-canvas");
  var types = STATE.relationships.types || {};
  var enabled = KG_REL_FILTER || Object.keys(types);
  var src = kgSources().filter(function(s){ return s.id===sourceId; })[0];
  if (!src || !src.tickers.length){ root.innerHTML = "<p class='muted small'>Empty basket.</p>"; return; }
  var inBasket = {}; src.tickers.forEach(function(t){ inBasket[t.toUpperCase()]=1; });

  // Include ANY tie that touches a basket member, so related companies OUTSIDE
  // the vertical (e.g., a utility's data-center customers) are pulled in to make
  // the web full and complete. External nodes are marked so they read distinctly.
  var relevant = {};
  (STATE.relationships.edges||[]).forEach(function(e){
    if (enabled.indexOf(e.type)===-1) return;
    if (inBasket[e.a] || inBasket[e.b]){ relevant[e.a]=1; relevant[e.b]=1; }
  });
  var edges = (STATE.relationships.edges||[]).filter(function(e){
    return enabled.indexOf(e.type)!==-1 && relevant[e.a] && relevant[e.b];
  });
  var nodes = Object.keys(relevant);
  // safety cap for very large scopes: keep basket members + highest-degree externals
  if (nodes.length > 46){
    var deg0 = {}; edges.forEach(function(e){ deg0[e.a]=(deg0[e.a]||0)+1; deg0[e.b]=(deg0[e.b]||0)+1; });
    var keep = {}; nodes.filter(function(n){ return inBasket[n]; }).forEach(function(n){ keep[n]=1; });
    var slots = Math.max(0, 46 - Object.keys(keep).length);
    nodes.filter(function(n){ return !inBasket[n]; }).sort(function(a,b){ return (deg0[b]||0)-(deg0[a]||0); }).slice(0, slots).forEach(function(n){ keep[n]=1; });
    nodes = nodes.filter(function(n){ return keep[n]; });
    edges = edges.filter(function(e){ return keep[e.a] && keep[e.b]; });
  }

  var legend = "<div class='row' id='kg-rel-filter' style='margin-bottom:6px'>" +
    Object.keys(types).map(function(t){
      var on = enabled.indexOf(t)!==-1;
      return "<span class='chip" + (on?" active":"") + "' data-rel-type='" + esc(t) + "' title='" + esc(types[t].desc) + "'><span class='badge-dot' style='background:" + types[t].color + "'></span>" + esc(types[t].label) + "</span>";
    }).join("") + "</div>";

  if (nodes.length < 2){
    root.innerHTML = legend + "<p class='muted small'>No curated relationships among the members of <b>" + esc(src.label) + "</b> yet. Try a vertical with dense ties like Semiconductors, AI Infrastructure, or Nuclear, or the Entire tracked market.</p>";
    bindBasketWebFilter(root, sourceId, enabled);
    return;
  }

  // market caps for node sizing (from baked fundamentals)
  Promise.all(nodes.map(function(t){ return getSeries(t).then(function(s){ return {t:t, cap:(s.fundamentals&&s.fundamentals.marketCap)||0}; }); })).then(function(caps){
    var capBy = {}; caps.forEach(function(c){ capBy[c.t]=c.cap; });
    var maxCap = Math.max.apply(null, caps.map(function(c){ return c.cap; }).concat([1]));

    // --- lightweight force-directed layout ---
    var W = 980, H = Math.max(520, 220 + nodes.length*12);
    var P = {}; nodes.forEach(function(n, i){ var a=(i/nodes.length)*Math.PI*2; P[n]={x:W/2+Math.cos(a)*180+ (Math.random()*20-10), y:H/2+Math.sin(a)*180+(Math.random()*20-10), vx:0, vy:0}; });
    var adj = {}; edges.forEach(function(e){ (adj[e.a]=adj[e.a]||[]).push(e.b); (adj[e.b]=adj[e.b]||[]).push(e.a); });
    var k = 170; // ideal edge length
    for (var iter=0; iter<220; iter++){
      // repulsion
      for (var i=0;i<nodes.length;i++){ for (var j=i+1;j<nodes.length;j++){
        var a=P[nodes[i]], b=P[nodes[j]];
        var dx=a.x-b.x, dy=a.y-b.y, d2=dx*dx+dy*dy+0.01, d=Math.sqrt(d2);
        var f = (k*k)/d2 * 0.9;
        var fx=dx/d*f, fy=dy/d*f;
        a.vx+=fx; a.vy+=fy; b.vx-=fx; b.vy-=fy;
      }}
      // attraction along edges
      edges.forEach(function(e){
        var a=P[e.a], b=P[e.b];
        var dx=b.x-a.x, dy=b.y-a.y, d=Math.sqrt(dx*dx+dy*dy)+0.01;
        var f=(d-k)/d * 0.06;
        var fx=dx*f, fy=dy*f;
        a.vx+=fx; a.vy+=fy; b.vx-=fx; b.vy-=fy;
      });
      // integrate + gravity to center + damping
      nodes.forEach(function(n){
        var p=P[n];
        p.vx += (W/2 - p.x)*0.004; p.vy += (H/2 - p.y)*0.004;
        p.x += Math.max(-14, Math.min(14, p.vx)); p.y += Math.max(-14, Math.min(14, p.vy));
        p.vx*=0.82; p.vy*=0.82;
        p.x=Math.max(40, Math.min(W-40, p.x)); p.y=Math.max(40, Math.min(H-40, p.y));
      });
    }

    // degree (dependency centrality) for labeling hubs
    var deg = {}; nodes.forEach(function(n){ deg[n]=(adj[n]||[]).length; });
    var hubs = nodes.slice().sort(function(a,b){ return deg[b]-deg[a]; }).slice(0,3);

    var svg = "<svg viewBox='0 0 " + W + " " + H + "' width='100%' style='max-height:" + H + "px'>" +
      "<defs><marker id='kgarrow2' markerWidth='9' markerHeight='9' refX='7' refY='3' orient='auto'><path d='M0,0 L7,3 L0,6 Z' fill='#93a2bb'/></marker></defs>";
    edges.forEach(function(e){
      var a=P[e.a], b=P[e.b]; var t=types[e.type]||{};
      var dx=b.x-a.x, dy=b.y-a.y, len=Math.sqrt(dx*dx+dy*dy)||1, ux=dx/len, uy=dy/len;
      var ra=14+Math.sqrt((capBy[e.a]||0)/maxCap)*16, rb=14+Math.sqrt((capBy[e.b]||0)/maxCap)*16;
      var x1=a.x+ux*ra, y1=a.y+uy*ra, x2=b.x-ux*(rb+4), y2=b.y-uy*(rb+4);
      svg += "<line x1='"+x1.toFixed(1)+"' y1='"+y1.toFixed(1)+"' x2='"+x2.toFixed(1)+"' y2='"+y2.toFixed(1)+"' stroke='"+(t.color||"#93a2bb")+"' stroke-opacity='.5' stroke-width='1.8'"+(t.directed?" marker-end='url(#kgarrow2)'":"")+"><title>"+esc(e.a+" -> "+e.b+": "+(t.label||e.type)+(e.note?(" ("+e.note+")"):""))+"</title></line>";
    });
    nodes.forEach(function(n){
      var p=P[n]; var rad=14+Math.sqrt((capBy[n]||0)/maxCap)*16;
      var isHub = hubs.indexOf(n)!==-1;
      var ext = !inBasket[n]; // related company pulled in from outside the basket
      var fill = isHub ? "rgba(79,209,197,.22)" : (ext ? "rgba(147,162,187,.10)" : "var(--panel2)");
      var stroke = isHub ? "#4fd1c5" : (ext ? "#3a4considered" : "#26324a");
      stroke = isHub ? "#4fd1c5" : (ext ? "#5b8cff" : "#26324a");
      svg += "<g class='kg-rnode' data-web-node='"+esc(n)+"' style='cursor:pointer'>" +
        "<circle cx='"+p.x.toFixed(1)+"' cy='"+p.y.toFixed(1)+"' r='"+rad.toFixed(1)+"' fill='"+fill+"' stroke='"+stroke+"' stroke-width='"+(isHub?2:1.4)+"'"+(ext?" stroke-dasharray='3,2'":"")+"/>" +
        "<text x='"+p.x.toFixed(1)+"' y='"+(p.y+4).toFixed(1)+"' text-anchor='middle' fill='"+(ext?"#c3ccd9":"#e7edf7")+"' font-size='11' font-weight='700'>"+esc(n)+"</text></g>";
    });
    svg += "</svg>";

    var extCount = nodes.filter(function(n){ return !inBasket[n]; }).length;
    root.innerHTML = legend +
      "<div class='flex-between'><h3 style='margin:2px 0'>" + esc(src.label) + " &mdash; relationship web (" + nodes.length + " companies, " + edges.length + " ties)</h3></div>" +
      "<p class='muted small' style='margin:0 0 6px'>Node size = market cap. Highlighted = the cluster&#39;s key dependencies. <span style='color:#5b8cff'>Dashed nodes</span> are related companies from outside this basket (customers, suppliers) pulled in to complete the picture. Click any node to focus its own web.</p>" +
      "<div style='overflow-x:auto'>" + svg + "</div>" +
      "<p class='footer-note'>Most-connected: <b>" + hubs.map(esc).join(", ") + "</b>" + (extCount?(" &middot; " + extCount + " related companies pulled in from outside the basket"):"") + ". Curated relationships as of " + esc(STATE.relationships.updated||"") + " &mdash; illustrative, not exhaustive.</p>";

    $all("[data-web-node]", root).forEach(function(el){ el.addEventListener("click", function(){ lsSet("kgTicker", el.getAttribute("data-web-node")); lsSet("kgRelScope","company"); showTab("moneyflow"); }); });
    bindBasketWebFilter(root, sourceId, enabled);
  }).catch(function(e){ console.error("GMR: basket web failed", e); root.innerHTML = legend + "<p class='muted small'>Could not build the web.</p>"; });
}
function bindBasketWebFilter(root, sourceId, enabled){
  $all("[data-rel-type]", root).forEach(function(chip){
    chip.addEventListener("click", function(){
      var t = chip.dataset.relType; var set = enabled.slice(); var i = set.indexOf(t);
      if (i===-1) set.push(t); else set.splice(i,1);
      KG_REL_FILTER = set.length ? set : Object.keys(STATE.relationships.types);
      renderBasketWeb(sourceId);
    });
  });
}

// Load SEC money-flow + sector for a set of tickers (skips those without data).
function loadBasketSEC(tickers){
  return Promise.all(tickers.map(function(t){
    return fetch("data/sec/" + encodeURIComponent(t) + ".json", {cache:"default"})
      .then(function(r){ return r.ok ? r.json() : null; })
      .catch(function(){ return null; })
      .then(function(sec){
        if (!sec || !(sec["in"]||{}).revenue) return null;
        // sector comes from baked fundamentals (via the quote file)
        return getSeries(t).then(function(s){ return { ticker:t, sec:sec, sector:((s.fundamentals||{}).sector)||"Other" }; });
      });
  })).then(function(rows){ return rows.filter(Boolean); });
}

function aggregateSEC(rows){
  var totalRev = 0, out = {}, net = 0, bySector = {};
  rows.forEach(function(r){
    var rev = (r.sec["in"]||{}).revenue || 0;
    totalRev += rev; net += (r.sec.net||0);
    var sec = bySector[r.sector] = bySector[r.sector] || {rev:0, out:{}, net:0, n:0, companies:[]};
    sec.rev += rev; sec.net += (r.sec.net||0); sec.n++;
    sec.companies.push({ ticker:r.ticker, rev:rev });
    Object.keys(r.sec.out||{}).forEach(function(k){
      out[k] = (out[k]||0) + r.sec.out[k];
      sec.out[k] = (sec.out[k]||0) + r.sec.out[k];
    });
  });
  return { totalRev:totalRev, out:out, net:net, bySector:bySector, n:rows.length };
}

function renderAggregateFlow(sourceId){
  var root = $("#kg-canvas");
  var src = kgSources().filter(function(s){ return s.id===sourceId; })[0];
  if (!src || !src.tickers.length){ root.innerHTML = "<p class='muted small'>Empty scope.</p>"; return; }
  root.innerHTML = "<p class='muted small'>Aggregating SEC filings across " + src.tickers.length + " companies" + (KG_AGG_SECTOR?(" &middot; " + esc(KG_AGG_SECTOR)):"") + "...</p>";
  loadBasketSEC(src.tickers).then(function(rows){
    if (!rows.length){ root.innerHTML = "<p class='muted small'>No SEC data available for this scope. Try an index or vertical of large US filers.</p>"; return; }
    var scoped = KG_AGG_SECTOR ? rows.filter(function(r){ return r.sector===KG_AGG_SECTOR; }) : rows;
    var agg = aggregateSEC(scoped);
    // pseudo "company" object for the Sankey drawer
    var d = { name: src.label + (KG_AGG_SECTOR?(" / " + KG_AGG_SECTOR):""), fy:"aggregate", "in":{revenue:agg.totalRev}, out:agg.out, net:agg.net };

    var crumb = "<div class='kg-crumb'>" +
      "<span class='" + (KG_AGG_SECTOR?"link":"") + "' id='kg-crumb-all'>" + esc(src.label) + "</span>" +
      (KG_AGG_SECTOR ? " &rsaquo; <span>" + esc(KG_AGG_SECTOR) + "</span>" : "") +
      "</div>";

    var svg = buildFlowSVG("MARKET", d, agg.totalRev);
    var title = KG_AGG_SECTOR ? (esc(KG_AGG_SECTOR) + " within " + esc(src.label)) : esc(src.label);

    // sector breakdown (only at top level)
    var sectorTable = "";
    if (!KG_AGG_SECTOR){
      var secs = Object.keys(agg.bySector).sort(function(a,b){ return agg.bySector[b].rev - agg.bySector[a].rev; });
      sectorTable = "<div class='section-title'>Where money flows by sector (click to drill in)</div>" +
        "<table><thead><tr><th>Sector</th><th>Cos</th><th>Revenue</th><th>R&amp;D</th><th>Capex</th><th>Shareholder returns</th><th>Net income</th></tr></thead><tbody>" +
        secs.map(function(sec){
          var s = agg.bySector[sec];
          var sr = (s.out.dividends||0) + (s.out.buybacks||0);
          return "<tr class='clickable' data-kg-sector='" + esc(sec) + "'><td><b>" + esc(sec) + "</b></td><td>" + s.n + "</td>" +
            "<td>$" + fmtBigPlain(s.rev) + "</td><td>$" + fmtBigPlain(s.out.rnd||0) + "</td><td>$" + fmtBigPlain(s.out.capex||0) + "</td>" +
            "<td>$" + fmtBigPlain(sr) + "</td><td class='" + (s.net>=0?"up":"down") + "'>$" + fmtBigPlain(s.net) + "</td></tr>";
        }).join("") + "</tbody></table>";
    }

    // company breakdown within current scope
    var companies = scoped.slice().sort(function(a,b){ return ((b.sec["in"]||{}).revenue||0) - ((a.sec["in"]||{}).revenue||0); }).slice(0, 20);
    var coTable = "<div class='section-title'>Companies " + (KG_AGG_SECTOR?"in this sector":"in this scope") + " (click to drill to their flow)</div>" +
      "<table><thead><tr><th>Ticker</th><th>Sector</th><th>Revenue</th><th>R&amp;D</th><th>Capex</th><th>Net income</th></tr></thead><tbody>" +
      companies.map(function(r){
        var o = r.sec.out||{};
        return "<tr class='clickable' data-kg-co='" + esc(r.ticker) + "'><td><b>" + esc(r.ticker) + "</b></td><td class='muted'>" + esc(r.sector) + "</td>" +
          "<td>$" + fmtBigPlain((r.sec["in"]||{}).revenue||0) + "</td><td>$" + fmtBigPlain(o.rnd||0) + "</td><td>$" + fmtBigPlain(o.capex||0) + "</td>" +
          "<td class='" + ((r.sec.net||0)>=0?"up":"down") + "'>$" + fmtBigPlain(r.sec.net||0) + "</td></tr>";
      }).join("") + "</tbody></table>";

    root.innerHTML = crumb +
      "<div class='flex-between'><h3 style='margin:6px 0'>" + title + " &mdash; aggregate money flow (" + scoped.length + " filers)</h3></div>" +
      "<div style='overflow-x:auto'>" + svg + "</div>" +
      "<p class='footer-note'>Aggregated from each company&#39;s latest annual SEC filing. Revenue on the left is the combined top line; the right shows combined cost of revenue, R&amp;D, SG&amp;A, taxes, net income, capex, dividends, and buybacks. R&amp;D + capex show where the group is <b>investing</b>; dividends + buybacks show capital <b>returned</b>.</p>" +
      sectorTable + coTable;

    var crumbAll = $("#kg-crumb-all"); if (crumbAll && KG_AGG_SECTOR) crumbAll.addEventListener("click", function(){ KG_AGG_SECTOR=null; renderAggregateFlow(sourceId); });
    $all("[data-kg-sector]", root).forEach(function(tr){ tr.addEventListener("click", function(){ KG_AGG_SECTOR = tr.dataset.kgSector; renderAggregateFlow(sourceId); }); });
    $all("[data-kg-co]", root).forEach(function(tr){ tr.addEventListener("click", function(){ lsSet("kgTicker", tr.dataset.kgCo); lsSet("kgMode","company"); showTab("moneyflow"); }); });
  }).catch(function(e){ console.error("GMR: aggregate flow failed", e); root.innerHTML = "<p class='muted small'>Could not aggregate SEC data.</p>"; });
}

function renderCompanyFlow(ticker){
  var root = $("#kg-canvas");
  root.innerHTML = "<p class='muted small'>Loading SEC filing data for " + esc(ticker) + "...</p>";
  fetch("data/sec/" + encodeURIComponent(ticker) + ".json", {cache:"default"})
    .then(function(r){ if(!r.ok) throw new Error("no SEC data"); return r.json(); })
    .then(function(d){ drawCompanyFlow(root, ticker, d); })
    .catch(function(){
      root.innerHTML = "<p class='muted small'>No SEC money-flow data for <b>" + esc(ticker) + "</b>. This is baked for tracked US filers " +
        "(foreign filers like some ADRs, and tickers outside the tracked set, may not report US-GAAP revenue). Try a large US name like NVDA, MSFT, or LLY.</p>";
    });
}

// Shared Sankey builder used by both the company and aggregate views.
function buildFlowSVG(centerLabel, d, rev){
  var outs = KG_OUT_META.map(function(m){
    var val = m[0]==="net" ? (d.net||0) : ((d.out||{})[m[0]]||0);
    return { key:m[0], label:m[1], color:m[2], val:val };
  }).filter(function(o){ return o.val && o.val > 0; });
  if (!rev || !outs.length) return "<p class='muted small'>No breakdown available.</p>";
  var maxOut = Math.max.apply(null, outs.map(function(o){ return o.val; }).concat([rev]));

  var W = 960, H = Math.max(360, 70 + outs.length*54), pad = 20;
  var revY = H/2, coW = 160, coH = 90, coY = H/2 - coH/2, coX = 290;
  var rightX = 640, nodeW = 250;
  var slotH = (H - 2*pad) / outs.length;
  function lw(v){ return Math.max(2, (v/maxOut) * 46); }
  var svg = "<svg viewBox='0 0 " + W + " " + H + "' width='100%' style='max-height:" + H + "px'>";
  outs.forEach(function(o, i){
    var y = pad + slotH*i + slotH/2;
    var x1 = coX + coW, x2 = rightX;
    svg += "<path d='M" + x1 + "," + revY + " C" + (x1+90) + "," + revY + " " + (x2-90) + "," + y + " " + x2 + "," + y + "' fill='none' stroke='" + o.color + "' stroke-opacity='.35' stroke-width='" + lw(o.val) + "'/>";
  });
  svg += "<path d='M120," + revY + " C200," + revY + " 220," + revY + " " + coX + "," + revY + "' fill='none' stroke='#3ecf8e' stroke-opacity='.4' stroke-width='" + lw(rev) + "'/>";
  svg += "<g><rect x='20' y='" + (revY-34) + "' width='100' height='68' rx='8' fill='rgba(62,207,142,.18)' stroke='#3ecf8e'/>" +
    "<text x='70' y='" + (revY-8) + "' text-anchor='middle' fill='#e7edf7' font-size='13' font-weight='700'>Revenue</text>" +
    "<text x='70' y='" + (revY+12) + "' text-anchor='middle' fill='#3ecf8e' font-size='13' font-weight='700'>$" + fmtBigPlain(rev) + "</text></g>";
  svg += "<g><rect x='" + coX + "' y='" + coY + "' width='" + coW + "' height='" + coH + "' rx='10' fill='var(--panel2)' stroke='#4fd1c5' stroke-width='1.5'/>" +
    "<text x='" + (coX+coW/2) + "' y='" + (coY+38) + "' text-anchor='middle' fill='#e7edf7' font-size='16' font-weight='800'>" + esc(centerLabel) + "</text>" +
    "<text x='" + (coX+coW/2) + "' y='" + (coY+60) + "' text-anchor='middle' fill='#93a2bb' font-size='11'>" + (d.fy==="aggregate"?"aggregate":("FY " + esc((d.fy||"").slice(0,4)))) + "</text></g>";
  outs.forEach(function(o, i){
    var y = pad + slotH*i + slotH/2;
    var pct = rev ? (o.val/rev*100) : 0;
    svg += "<g><rect x='" + rightX + "' y='" + (y-18) + "' width='" + nodeW + "' height='36' rx='7' fill='" + o.color + "' fill-opacity='.16' stroke='" + o.color + "' stroke-opacity='.6'/>" +
      "<text x='" + (rightX+12) + "' y='" + (y+5) + "' fill='#e7edf7' font-size='12.5' font-weight='700'>" + esc(o.label) + "</text>" +
      "<text x='" + (rightX+nodeW-12) + "' y='" + (y+5) + "' text-anchor='end' fill='#e7edf7' font-size='12.5'>$" + fmtBigPlain(o.val) + " &#183; " + pct.toFixed(0) + "%</text></g>";
  });
  svg += "</svg>";
  return svg;
}

function drawCompanyFlow(root, ticker, d){
  var rev = (d["in"]||{}).revenue || 0;
  if (!rev){ root.innerHTML = "<p class='muted small'>No revenue reported for " + esc(ticker) + ".</p>"; return; }
  var svg = buildFlowSVG(ticker, d, rev);
  root.innerHTML =
    "<div class='flex-between'><h3 style='margin:0'>" + esc(d.name||ticker) + " &mdash; money flow (FY " + esc((d.fy||"").slice(0,4)) + ")</h3>" +
      "<button class='btn small ghost' id='kg-open-co'>Open " + esc(ticker) + " &rarr;</button></div>" +
    "<div style='overflow-x:auto'>" + svg + "</div>" +
    "<p class='footer-note'>Money in (revenue) on the left flows through " + esc(ticker) + " to its cost, investment, and capital-return allocations on the right. " +
      "Percentages are of revenue. Income-statement items (cost of revenue, R&amp;D, SG&amp;A, interest, taxes, net income) and cash-flow items " +
      "(capex, dividends, buybacks) are both shown. Source: SEC XBRL company facts, latest annual filing.</p>";
  var ob = $("#kg-open-co"); if (ob) ob.addEventListener("click", function(){ CO_TICKER = ticker; lsSet("companiesTicker", ticker); showTab("companies"); });
}

// compact $ for SVG labels (no leading $)
function fmtBigPlain(v){
  var a = Math.abs(v);
  if (a >= 1e12) return (v/1e12).toFixed(1) + "T";
  if (a >= 1e9) return (v/1e9).toFixed(1) + "B";
  if (a >= 1e6) return (v/1e6).toFixed(0) + "M";
  return String(Math.round(v));
}

function renderBasketNetwork(sourceId){
  var root = $("#kg-canvas");
  var src = heatSources().filter(function(s){ return s.id===sourceId; })[0];
  if (!src || !src.tickers.length){ root.innerHTML = "<p class='muted small'>Empty basket.</p>"; return; }
  root.innerHTML = "<p class='muted small'>Building network...</p>";
  Promise.all(src.tickers.map(function(t){ return getSeries(t).then(function(s){ return {t:t, s:s}; }); })).then(function(rows){
    // node = company; color by money-flow (CMF), size by market cap; clustered by sector
    var bySector = {};
    rows.forEach(function(r){
      var f = r.s.fundamentals || {};
      var sector = f.sector || "Other";
      var cmf = IND.cmf(r.s.dates, r.s.closes, r.s.volumes, 21);
      var status = IND.moneyFlowStatus(cmf, 21);
      (bySector[sector] = bySector[sector] || []).push({ ticker:r.t, cap:f.marketCap||0, flow:status });
    });
    var sectors = Object.keys(bySector);
    var W = 960, H = Math.max(420, sectors.length*150), cxHub = W/2, cyHub = H/2;
    var svg = "<svg viewBox='0 0 " + W + " " + H + "' width='100%' style='max-height:" + H + "px'>";
    var hubR = 34;
    // sector hubs around center
    var secPos = {};
    sectors.forEach(function(sec, i){
      var ang = (i/sectors.length)*Math.PI*2 - Math.PI/2;
      var r = Math.min(W,H)*0.30;
      var x = cxHub + Math.cos(ang)*r, y = cyHub + Math.sin(ang)*r;
      secPos[sec] = {x:x, y:y, ang:ang};
      svg += "<line x1='" + cxHub + "' y1='" + cyHub + "' x2='" + x + "' y2='" + y + "' stroke='#26324a' stroke-width='1.5'/>";
    });
    // company nodes around each sector hub
    sectors.forEach(function(sec){
      var hub = secPos[sec];
      var items = bySector[sec];
      var maxCap = Math.max.apply(null, items.map(function(it){ return it.cap||0; }).concat([1]));
      items.forEach(function(it, j){
        var a = hub.ang + (j - (items.length-1)/2) * 0.5;
        var rr = 88 + (items.length>6? (j%2)*34 : 0);
        var x = hub.x + Math.cos(a)*rr, y = hub.y + Math.sin(a)*rr;
        var rad = 10 + Math.sqrt((it.cap||0)/maxCap)*20;
        var col = it.flow.cls==="up" ? "#3ecf8e" : (it.flow.cls==="down" ? "#f56565" : "#93a2bb");
        svg += "<line x1='" + hub.x + "' y1='" + hub.y + "' x2='" + x + "' y2='" + y + "' stroke='" + col + "' stroke-opacity='.35' stroke-width='1.5'/>";
        svg += "<g class='kg-cnode' data-kg-node='" + esc(it.ticker) + "' style='cursor:pointer'>" +
          "<circle cx='" + x + "' cy='" + y + "' r='" + rad.toFixed(1) + "' fill='" + col + "' fill-opacity='.22' stroke='" + col + "' stroke-width='1.5'/>" +
          "<text x='" + x + "' y='" + (y+4) + "' text-anchor='middle' fill='#e7edf7' font-size='11' font-weight='700'>" + esc(it.ticker) + "</text></g>";
      });
    });
    // sector hubs on top
    sectors.forEach(function(sec){
      var hub = secPos[sec];
      svg += "<g><circle cx='" + hub.x + "' cy='" + hub.y + "' r='" + hubR + "' fill='var(--panel2)' stroke='#4fd1c5' stroke-width='1.5'/>" +
        "<text x='" + hub.x + "' y='" + (hub.y+4) + "' text-anchor='middle' fill='#4fd1c5' font-size='10.5' font-weight='700'>" + esc(sec.length>12?sec.slice(0,11)+"…":sec) + "</text></g>";
    });
    // center hub
    svg += "<circle cx='" + cxHub + "' cy='" + cyHub + "' r='30' fill='#4fd1c5' fill-opacity='.15' stroke='#4fd1c5'/>" +
      "<text x='" + cxHub + "' y='" + (cyHub+4) + "' text-anchor='middle' fill='#e7edf7' font-size='11' font-weight='800'>" + esc(src.label.split(":")[0]) + "</text>";
    svg += "</svg>";
    root.innerHTML =
      "<div style='overflow-x:auto'>" + svg + "</div>" +
      "<p class='footer-note'>Companies clustered by sector. Node size = market cap; " +
      "<span style='color:#3ecf8e'>green</span> = money accumulating (positive Chaikin Money Flow), " +
      "<span style='color:#f56565'>red</span> = distributing, grey = neutral. Click a node to open it.</p>";
    $all("[data-kg-node]", root).forEach(function(el){ el.addEventListener("click", function(){ CO_TICKER = el.getAttribute("data-kg-node"); lsSet("companiesTicker", CO_TICKER); showTab("companies"); }); });
  }).catch(function(e){ console.error("GMR: basket network failed", e); root.innerHTML = "<p class='muted small'>Could not build the network.</p>"; });
}
"""

APP_JS = JS_OPEN + JS_CORE + JS_PROXY + JS_ROUTER + JS_DASHBOARD + JS_WATCHLISTS + JS_CHART + JS_COMPANIES + JS_OPTIMIZER + JS_BACKTEST + JS_UPDATES + JS_PREIPO + JS_PROFILE + JS_GITHUB + JS_ALERTS + JS_METHODOLOGY + JS_INDEXES + JS_HEATMAP + JS_KG + JS_CLOSE


if __name__ == "__main__":
    build()
