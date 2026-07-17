#!/usr/bin/env python3
"""Build the PIR Workbench (P9) — a self-contained, read-only inspector page.

Reads the exported PIR view bundle and inlines it into a single HTML file
(`build/pir_view/workbench.html`, gitignored) with all CSS/JS embedded — no
external requests, CSP-safe, publishable as an Artifact or openable in a browser.
The page renders the six surfaces from `docs/pir-p9-workbench-scope.md`:

  facts table (L⟂E orthogonal, verdict, SOUND/HEURISTIC honesty) · verdict×evidence
  matrix · provenance/invalidation · candidate lattice · cross-domain diff ·
  structural graph.

Read-only: the page renders committed data and never writes a fact, verdict, or
certificate. Regenerate the bundle first with `python3 ci/export_pir_view.py`.
"""

from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from ci.export_pir_view import build_bundle

# The page body (no <!doctype>/<html>/<head>/<body> — Artifact adds the skeleton,
# and browsers wrap a bare fragment fine for local file:// viewing).
PAGE = r"""
<style>
:root{
  --sans: system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
  --mono: ui-monospace,"SF Mono","JetBrains Mono",Menlo,Consolas,monospace;
  /* neutrals carry a slight cool (cyan) bias — chosen, not defaulted */
  --ground:#0c0f14; --surface:#12171f; --surface2:#171e28; --raised:#1c2531;
  --ink:#e6edf3; --ink-muted:#9aa7b4; --ink-faint:#63707e; --border:#232c38;
  --accent:#39b6c8; --accent-dim:#1f6673; --focus:#5fd0e0;
  /* verdict status hues (always shown WITH the verdict word — never color-alone) */
  --v-forced:#3aae55; --v-permitted:#5290df; --v-rejected:#ec5860;
  --v-nonident:#d99a24; --v-repdep:#a878f2; --v-neutral:#7d8b9c; --v-none:#556170;
  /* evidence sequential ramp: E0 exact (strong/saturated) -> E4 proxy (faded) */
  --e0:#2bb7c9; --e1:#3f9fb4; --e2:#5d8a9e; --e3:#6f7d8c; --e4:#5a6472;
  --good:#3aae55; --warn:#d99a24; --crit:#ec5860;
  --shadow:0 1px 0 rgba(0,0,0,.4),0 8px 30px rgba(0,0,0,.35);
}
@media (prefers-color-scheme: light){:root{
  --ground:#eef1f4; --surface:#ffffff; --surface2:#f5f7f9; --raised:#ffffff;
  --ink:#16202b; --ink-muted:#4f5d6b; --ink-faint:#8290a0; --border:#dde3ea;
  --accent:#0f7c8c; --accent-dim:#bfe0e6; --focus:#0f7c8c;
  --v-forced:#1f8a3f; --v-permitted:#2b6fc4; --v-rejected:#cf3b43;
  --v-nonident:#a5760d; --v-repdep:#7d4fd0; --v-neutral:#5c6a79; --v-none:#8695a4;
  --e0:#0e8494; --e1:#2f7e8e; --e2:#4c7385; --e3:#657687; --e4:#8090a0;
  --shadow:0 1px 0 rgba(16,32,48,.03),0 8px 26px rgba(16,32,48,.08);
}}
:root[data-theme="dark"]{
  --ground:#0c0f14; --surface:#12171f; --surface2:#171e28; --raised:#1c2531;
  --ink:#e6edf3; --ink-muted:#9aa7b4; --ink-faint:#63707e; --border:#232c38;
  --accent:#39b6c8; --accent-dim:#1f6673; --focus:#5fd0e0;
  --v-forced:#3aae55; --v-permitted:#5290df; --v-rejected:#ec5860;
  --v-nonident:#d99a24; --v-repdep:#a878f2; --v-neutral:#7d8b9c; --v-none:#556170;
  --e0:#2bb7c9; --e1:#3f9fb4; --e2:#5d8a9e; --e3:#6f7d8c; --e4:#5a6472;
}
:root[data-theme="light"]{
  --ground:#eef1f4; --surface:#ffffff; --surface2:#f5f7f9; --raised:#ffffff;
  --ink:#16202b; --ink-muted:#4f5d6b; --ink-faint:#8290a0; --border:#dde3ea;
  --accent:#0f7c8c; --accent-dim:#bfe0e6; --focus:#0f7c8c;
  --v-forced:#1f8a3f; --v-permitted:#2b6fc4; --v-rejected:#cf3b43;
  --v-nonident:#a5760d; --v-repdep:#7d4fd0; --v-neutral:#5c6a79; --v-none:#8695a4;
  --e0:#0e8494; --e1:#2f7e8e; --e2:#4c7385; --e3:#657687; --e4:#8090a0;
}
*{box-sizing:border-box}
#pir{font-family:var(--sans);background:var(--ground);color:var(--ink);
  min-height:100vh;font-size:14px;line-height:1.5;-webkit-font-smoothing:antialiased}
#pir .mono{font-family:var(--mono);font-variant-numeric:tabular-nums}
#pir a{color:var(--accent)}
#pir h1,#pir h2,#pir h3{margin:0;text-wrap:balance;font-weight:620;letter-spacing:-.01em}
#pir .layout{display:grid;grid-template-columns:248px minmax(0,1fr);min-height:100vh}
/* rail */
#pir .rail{background:var(--surface);border-right:1px solid var(--border);
  padding:20px 16px;display:flex;flex-direction:column;gap:18px;position:sticky;top:0;height:100vh;overflow:auto}
#pir .brand{display:flex;flex-direction:column;gap:3px}
#pir .brand .k{font-family:var(--mono);font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--accent)}
#pir .brand h1{font-size:19px}
#pir .brand .sub{color:var(--ink-faint);font-size:12px}
#pir nav{display:flex;flex-direction:column;gap:2px}
#pir nav button{all:unset;cursor:pointer;display:flex;align-items:center;gap:10px;
  padding:8px 10px;border-radius:7px;color:var(--ink-muted);font-size:13px;font-weight:520}
#pir nav button:hover{background:var(--surface2);color:var(--ink)}
#pir nav button[aria-current="true"]{background:var(--accent-dim);color:var(--ink)}
#pir nav button .idx{font-family:var(--mono);font-size:11px;color:var(--ink-faint);width:14px}
#pir nav button[aria-current="true"] .idx{color:var(--accent)}
#pir .rail .glance{border-top:1px solid var(--border);padding-top:14px;display:flex;flex-direction:column;gap:9px}
#pir .glance .row{display:flex;justify-content:space-between;align-items:baseline;font-size:12px}
#pir .glance .row .n{font-family:var(--mono);font-size:18px;color:var(--ink)}
#pir .glance .row .l{color:var(--ink-faint);text-transform:uppercase;letter-spacing:.08em;font-size:10px}
#pir .legend{border-top:1px solid var(--border);padding-top:14px;font-size:11.5px;color:var(--ink-muted)}
#pir .legend b{color:var(--ink);font-weight:600}
#pir .legend .ln{display:flex;gap:7px;align-items:center;margin-top:6px}
#pir .theme{all:unset;cursor:pointer;margin-top:auto;color:var(--ink-faint);font-size:12px;
  border:1px solid var(--border);border-radius:7px;padding:7px 10px;text-align:center}
#pir .theme:hover{color:var(--ink);border-color:var(--accent-dim)}
/* main */
#pir main{padding:26px 30px 60px;max-width:1180px}
#pir .surface-head{margin-bottom:18px}
#pir .surface-head h2{font-size:22px}
#pir .surface-head p{color:var(--ink-muted);margin:6px 0 0;max-width:64ch}
#pir .panel{background:var(--surface);border:1px solid var(--border);border-radius:12px;box-shadow:var(--shadow)}
#pir .pad{padding:18px}
#pir .grid{display:grid;gap:16px}
/* summary strip */
#pir .strip{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:22px}
#pir .strip .cap{font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-faint);margin-bottom:10px}
#pir .distbar{display:flex;height:26px;border-radius:6px;overflow:hidden;gap:2px;background:transparent}
#pir .distbar > div{display:flex;align-items:center;justify-content:center;min-width:2px;color:#fff;
  font-family:var(--mono);font-size:11px}
#pir .dist-key{display:flex;flex-wrap:wrap;gap:10px 16px;margin-top:12px;font-size:12px;color:var(--ink-muted)}
#pir .dist-key .sw{width:9px;height:9px;border-radius:2px;display:inline-block;margin-right:6px;vertical-align:middle}
#pir .eladder{display:flex;gap:8px}
#pir .eladder .e{flex:1;border-radius:8px;padding:10px;color:#04121a;text-align:center}
#pir .eladder .e .n{font-family:var(--mono);font-size:20px;font-weight:600;display:block}
#pir .eladder .e .l{font-size:10px;letter-spacing:.06em;opacity:.85}
/* pills / chips */
#pir .pill{font-family:var(--mono);font-size:11px;padding:2px 8px;border-radius:20px;
  border:1px solid;white-space:nowrap;font-weight:600;letter-spacing:.02em}
#pir .chip{font-family:var(--mono);font-size:11px;padding:2px 7px;border-radius:5px;
  background:var(--surface2);border:1px solid var(--border);color:var(--ink-muted)}
#pir .ebadge{font-family:var(--mono);font-size:11px;font-weight:700;padding:2px 7px;border-radius:5px;color:#04121a}
#pir .tag{font-family:var(--mono);font-size:10px;font-weight:700;letter-spacing:.06em;padding:2px 7px;border-radius:5px;text-transform:uppercase}
#pir .tag.sound{background:color-mix(in srgb,var(--good) 18%,transparent);color:var(--good);border:1px solid color-mix(in srgb,var(--good) 40%,transparent)}
#pir .tag.heuristic{background:color-mix(in srgb,var(--warn) 18%,transparent);color:var(--warn);border:1px solid color-mix(in srgb,var(--warn) 45%,transparent)}
/* facts table */
#pir .filters{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-bottom:14px}
#pir .filters select,#pir .filters input{font-family:var(--sans);font-size:13px;background:var(--surface);
  color:var(--ink);border:1px solid var(--border);border-radius:7px;padding:7px 10px}
#pir .filters input{min-width:180px}
#pir .filters .count{margin-left:auto;color:var(--ink-faint);font-size:12px;font-family:var(--mono)}
#pir table{width:100%;border-collapse:collapse;font-size:13px}
#pir thead th{text-align:left;font-size:10px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-faint);
  font-weight:600;padding:0 12px 10px;border-bottom:1px solid var(--border);position:sticky;top:0;background:var(--surface)}
#pir tbody tr{border-bottom:1px solid var(--border);cursor:pointer}
#pir tbody tr:hover{background:var(--surface2)}
#pir tbody td{padding:9px 12px;vertical-align:middle}
#pir tbody tr.heuristic td:first-child{box-shadow:inset 3px 0 0 var(--warn)}
#pir tbody tr.sound td:first-child{box-shadow:inset 3px 0 0 color-mix(in srgb,var(--good) 55%,transparent)}
#pir td .fid{color:var(--ink-muted);font-size:12px}
#pir .LE{font-family:var(--mono);font-size:12px}
#pir .LE b{color:var(--ink)}
#pir .warn-dot{color:var(--warn);font-family:var(--mono)}
#pir .detail{background:var(--surface2)}
#pir .detail td{padding:14px 18px}
#pir .detail .kv{display:grid;grid-template-columns:120px 1fr;gap:6px 16px;font-size:12.5px}
#pir .detail .kv .k{color:var(--ink-faint);font-family:var(--mono)}
#pir pre{font-family:var(--mono);font-size:12px;background:var(--ground);border:1px solid var(--border);
  border-radius:8px;padding:12px;overflow:auto;margin:8px 0 0;color:var(--ink-muted)}
#pir .taint{display:inline-flex;gap:6px;flex-wrap:wrap}
#pir .taint .t{font-family:var(--mono);font-size:11px;padding:2px 7px;border-radius:5px;
  background:color-mix(in srgb,var(--warn) 14%,transparent);color:var(--warn);border:1px solid color-mix(in srgb,var(--warn) 35%,transparent)}
/* matrix */
#pir .matrix{border-collapse:separate;border-spacing:4px}
#pir .matrix td,#pir .matrix th{text-align:center;font-family:var(--mono);font-size:12px}
#pir .matrix th{color:var(--ink-faint);font-weight:600;padding:4px}
#pir .matrix .rowh{text-align:right;padding-right:10px;color:var(--ink);white-space:nowrap}
#pir .matrix .cell{width:62px;height:40px;border-radius:7px;color:#04121a;font-weight:700;
  display:flex;align-items:center;justify-content:center;border:1px solid var(--border)}
#pir .matrix .cell.zero{background:var(--surface2)!important;color:var(--ink-faint);font-weight:400}
#pir .matrix .tot{color:var(--ink-muted);font-weight:600}
#pir .ramp{display:flex;align-items:center;gap:8px;margin-top:14px;font-size:11px;color:var(--ink-faint)}
#pir .ramp .bar{display:flex;height:10px;border-radius:5px;overflow:hidden}
#pir .ramp .bar i{width:26px;height:10px}
/* provenance */
#pir .prov{display:grid;grid-template-columns:260px 1fr;gap:16px}
#pir .asmlist{display:flex;flex-direction:column;gap:4px;max-height:520px;overflow:auto}
#pir .asmlist button{all:unset;cursor:pointer;display:flex;justify-content:space-between;gap:10px;
  padding:7px 10px;border-radius:7px;font-family:var(--mono);font-size:12px;color:var(--ink-muted)}
#pir .asmlist button:hover{background:var(--surface2);color:var(--ink)}
#pir .asmlist button[aria-current="true"]{background:var(--accent-dim);color:var(--ink)}
#pir .asmlist button .c{color:var(--ink-faint)}
#pir .callout{border-left:3px solid var(--warn);background:color-mix(in srgb,var(--warn) 9%,transparent);
  padding:12px 14px;border-radius:0 8px 8px 0;font-size:13px;margin-bottom:14px}
/* diff gauges */
#pir .gauges{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px}
#pir .gauge{text-align:center;padding:20px}
#pir .gauge .v{font-family:var(--mono);font-size:40px;font-weight:600;color:var(--accent)}
#pir .gauge .l{font-size:11px;letter-spacing:.09em;text-transform:uppercase;color:var(--ink-faint);margin-top:4px}
#pir .gauge .track{height:8px;border-radius:4px;background:var(--surface2);margin-top:14px;overflow:hidden}
#pir .gauge .track i{display:block;height:8px;background:var(--accent);border-radius:4px}
#pir .motifs{display:flex;flex-wrap:wrap;gap:8px;margin-top:8px}
#pir .motifs .m{font-family:var(--mono);font-size:12px;padding:3px 9px;border-radius:6px}
#pir .motifs .m.shared{background:color-mix(in srgb,var(--good) 15%,transparent);color:var(--good);border:1px solid color-mix(in srgb,var(--good) 35%,transparent)}
#pir .motifs .m.diverge{background:color-mix(in srgb,var(--v-repdep) 15%,transparent);color:var(--v-repdep);border:1px solid color-mix(in srgb,var(--v-repdep) 35%,transparent)}
/* graph */
#pir svg{width:100%;height:auto;display:block}
#pir .tooltip{position:fixed;pointer-events:none;background:var(--raised);border:1px solid var(--border);
  border-radius:8px;padding:8px 10px;font-family:var(--mono);font-size:12px;box-shadow:var(--shadow);
  opacity:0;transition:opacity .1s;z-index:50;max-width:280px;color:var(--ink)}
#pir .hide{display:none!important}
#pir .muted{color:var(--ink-muted)}
#pir button:focus-visible,#pir select:focus-visible,#pir input:focus-visible{outline:2px solid var(--focus);outline-offset:2px}
@media (max-width:820px){#pir .layout{grid-template-columns:1fr}#pir .rail{position:static;height:auto;flex-direction:row;flex-wrap:wrap}#pir .prov,#pir .strip,#pir .gauges{grid-template-columns:1fr}}
</style>

<div id="pir">
  <div class="layout">
    <aside class="rail">
      <div class="brand">
        <span class="k">PIR · workbench</span>
        <h1>Evidence substrate</h1>
        <span class="sub">read-only view of the decompiled corpus</span>
      </div>
      <nav id="nav"></nav>
      <div class="glance" id="glance"></div>
      <div class="legend" id="legend"></div>
      <button class="theme" id="themeBtn">◐ theme</button>
    </aside>
    <main id="main"></main>
  </div>
  <div class="tooltip" id="tip"></div>
</div>

<script id="pir-data" type="application/json">__PIR_DATA__</script>
<script>
(function(){
  "use strict";
  var DATA = JSON.parse(document.getElementById("pir-data").textContent);
  var $ = function(s,r){return (r||document).querySelector(s);};
  var el = function(t,c,h){var e=document.createElement(t);if(c)e.className=c;if(h!=null)e.innerHTML=h;return e;};
  var esc = function(s){return String(s==null?"":s).replace(/[&<>"]/g,function(m){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[m];});};

  var VCOLOR = {FORCED:"--v-forced",PERMITTED:"--v-permitted",REJECTED:"--v-rejected",
    NONIDENTIFIABLE:"--v-nonident",REPRESENTATION_DEPENDENT:"--v-repdep",
    OBSERVATIONALLY_EQUIVALENT:"--v-neutral",APPARATUS_LIMITED:"--v-neutral",
    AMBIGUOUS:"--v-neutral"};
  var ECOLOR = {E0:"--e0",E1:"--e1",E2:"--e2",E3:"--e3",E4:"--e4"};
  var EMEAN = {E0:"exact",E1:"interval",E2:"statistical",E3:"simulation",E4:"proxy"};
  function vcol(v){return "var("+(VCOLOR[v]||"--v-none")+")";}
  function pill(v){if(!v)return '<span class="pill" style="color:var(--v-none);border-color:var(--v-none)">—</span>';
    var c=vcol(v);return '<span class="pill" style="color:'+c+';border-color:'+c+';background:color-mix(in srgb,'+c+' 12%,transparent)">'+esc(v)+'</span>';}
  function ebadge(e){return '<span class="ebadge" style="background:var('+(ECOLOR[e]||"--e4")+')">'+esc(e)+'</span>';}

  var SURFACES = [
    {id:"facts",name:"Facts",fn:renderFacts,
     desc:"Every lowered fact. L (representation) and E (warrant) are orthogonal axes; the SOUND/HEURISTIC tag and evidence level are shown so no simulation-conditioned result reads as a certificate."},
    {id:"matrix",name:"Verdict × evidence",fn:renderMatrix,
     desc:"How the corpus distributes across verdicts and warrant levels. Cell shade encodes count (one sequential ramp)."},
    {id:"prov",name:"Provenance",fn:renderProv,
     desc:"Assumption-taint and invalidation. Selecting an assumption shows the facts that rest on it; withdrawing one downgrades exactly its dependents — nothing is deleted."},
    {id:"lattice",name:"Candidate lattice",fn:renderLattice,
     desc:"Competing grammar families retained in parallel, with the interventions that would discriminate them."},
    {id:"diff",name:"Cross-domain diff",fn:renderDiff,
     desc:"Feature-level comparison of two domains. Similarity and confidence are reported separately with a named correlator — no ontology-identity claim."},
    {id:"graph",name:"Structural graph",fn:renderGraph,
     desc:"The B9 act-trace: nodes are operational acts, edges are time ordering and shared coordinates."}
  ];

  function facts(){return DATA.facts||[];}

  // ---- rail -------------------------------------------------------------
  function buildRail(){
    var nav=$("#nav");
    SURFACES.forEach(function(s,i){
      var b=el("button",null,'<span class="idx">'+(i+1)+'</span>'+esc(s.name));
      b.setAttribute("data-s",s.id);
      b.onclick=function(){go(s.id);};
      nav.appendChild(b);
    });
    var g=$("#glance"), d=DATA.distributions||{verdicts:{},evidence_levels:{}};
    var nb=Object.keys(DATA.coverage||{}).length;
    g.innerHTML='<div class="row"><span class="n">'+facts().length+'</span><span class="l">facts</span></div>'
      +'<div class="row"><span class="n">'+nb+'</span><span class="l">benchmarks</span></div>'
      +'<div class="row"><span class="n">'+Object.keys(d.verdicts||{}).filter(function(k){return k!=="(none)";}).length+'</span><span class="l">verdict kinds</span></div>';
    $("#legend").innerHTML='<b>Reading the badges</b>'
      +'<div class="ln"><span class="tag sound">SOUND</span> certifies what it asserts</div>'
      +'<div class="ln"><span class="tag heuristic">HEURISTIC</span> model-conditioned; carries a warning</div>'
      +'<div class="ln" style="margin-top:8px">'+["E0","E1","E2","E3","E4"].map(function(e){return ebadge(e);}).join(" ")+'</div>'
      +'<div class="ln muted" style="display:block">E0 exact → E4 proxy. An E3/E4 result is never a certificate.</div>';
    $("#themeBtn").onclick=toggleTheme;
  }

  // ---- surfaces ---------------------------------------------------------
  var STATE={s:"facts",fv:"",fe:"",ft:"",fq:"",asm:null,open:{}};
  function go(id){STATE.s=id;render();history.replaceState(null,"","#"+id);}
  function summaryStrip(){
    var d=DATA.distributions||{verdicts:{},evidence_levels:{}};
    var vt=facts().length||1;
    var order=["FORCED","PERMITTED","REJECTED","NONIDENTIFIABLE","REPRESENTATION_DEPENDENT","OBSERVATIONALLY_EQUIVALENT","(none)"];
    var segs=order.filter(function(k){return d.verdicts[k];}).map(function(k){
      var w=(d.verdicts[k]/vt*100).toFixed(2), c=k==="(none)"?"var(--v-none)":vcol(k);
      return '<div title="'+esc(k)+': '+d.verdicts[k]+'" style="flex:'+d.verdicts[k]+' 0 0;background:'+c+'">'+(d.verdicts[k]/vt>0.06?d.verdicts[k]:"")+'</div>';
    }).join("");
    var key=order.filter(function(k){return d.verdicts[k];}).map(function(k){
      var c=k==="(none)"?"var(--v-none)":vcol(k);
      return '<span><span class="sw" style="background:'+c+'"></span>'+esc(k.toLowerCase())+' <b class="mono">'+d.verdicts[k]+'</b></span>';
    }).join("");
    var eL=["E0","E1","E2","E3","E4"].map(function(e){
      var n=d.evidence_levels[e]||0;
      return '<div class="e" style="background:var('+ECOLOR[e]+')"><span class="n">'+n+'</span><span class="l">'+e+' · '+EMEAN[e]+'</span></div>';
    }).join("");
    return '<div class="strip">'
      +'<div class="panel pad"><div class="cap">verdict distribution</div><div class="distbar">'+segs+'</div><div class="dist-key">'+key+'</div></div>'
      +'<div class="panel pad"><div class="cap">warrant (evidence level)</div><div class="eladder">'+eL+'</div></div>'
      +'</div>';
  }

  function renderFacts(m){
    var fs=facts();
    var verds=Array.from(new Set(fs.map(function(f){return f.verdict||"(none)";}))).sort();
    var bar='<div class="filters">'
      +'<select id="fv"><option value="">all verdicts</option>'+verds.map(function(v){return '<option '+(STATE.fv===v?"selected":"")+'>'+esc(v)+'</option>';}).join("")+'</select>'
      +'<select id="fe"><option value="">all evidence</option>'+["E0","E1","E2","E3","E4"].map(function(e){return '<option '+(STATE.fe===e?"selected":"")+'>'+e+'</option>';}).join("")+'</select>'
      +'<select id="ft"><option value="">SOUND + HEURISTIC</option><option '+(STATE.ft==="SOUND"?"selected":"")+'>SOUND</option><option '+(STATE.ft==="HEURISTIC"?"selected":"")+'>HEURISTIC</option></select>'
      +'<input id="fq" placeholder="search subject / id" value="'+esc(STATE.fq)+'">'
      +'<span class="count" id="fcount"></span></div>';
    var rows=fs.filter(function(f){
      if(STATE.fv&&(f.verdict||"(none)")!==STATE.fv)return false;
      if(STATE.fe&&f.evidence_level!==STATE.fe)return false;
      if(STATE.ft&&f.analyzer.tag!==STATE.ft)return false;
      if(STATE.fq){var q=STATE.fq.toLowerCase();if((f.fact_id+" "+(f.content.subject||"")).toLowerCase().indexOf(q)<0)return false;}
      return true;
    });
    var body=rows.map(function(f){
      var tag=f.analyzer.tag.toLowerCase();
      var subj=f.content.subject||f.source_spans[0].span;
      var warn=(f.warnings&&f.warnings.length)?' <span class="warn-dot" title="'+esc(f.warnings[0].message)+'">▲</span>':"";
      var tr='<tr class="'+tag+'" data-id="'+esc(f.fact_id)+'">'
        +'<td><div>'+pill(f.verdict)+warn+'</div><div class="fid mono">'+esc(f.fact_id)+'</div></td>'
        +'<td class="mono">'+esc(subj)+'</td>'
        +'<td>'+ebadge(f.evidence_level)+'</td>'
        +'<td class="LE"><b>'+esc(f.pir_level)+'</b> · '+esc(f.layer.toLowerCase())+'</td>'
        +'<td class="mono muted">'+esc(f.namespace)+'</td>'
        +'<td><span class="tag '+tag+'">'+esc(f.analyzer.tag)+'</span></td></tr>';
      if(STATE.open[f.fact_id]){
        var asm=(f.assumptions||[]).map(function(a){return '<span class="t">'+esc(a)+'</span>';}).join("")||'<span class="muted">none</span>';
        var wit=f.witness?('<pre>'+esc(JSON.stringify(f.witness,null,1))+'</pre>'):"";
        var imp=f.impossibility_certificate?('<pre>'+esc(JSON.stringify(f.impossibility_certificate,null,1))+'</pre>'):"";
        tr+='<tr class="detail"><td colspan="6"><div class="kv">'
          +'<span class="k">content</span><div><pre>'+esc(JSON.stringify(f.content,null,1))+'</pre></div>'
          +'<span class="k">assumptions</span><div class="taint">'+asm+'</div>'
          +(f.measurement_interface&&f.measurement_interface.length?'<span class="k">𝖬 interface</span><div class="mono muted">'+esc(f.measurement_interface.join(", "))+'</div>':"")
          +(wit?'<span class="k">witness</span><div>'+wit+'</div>':"")
          +(imp?'<span class="k">impossibility</span><div>'+imp+'</div>':"")
          +'</div></td></tr>';
      }
      return tr;
    }).join("");
    m.innerHTML=bar+'<div class="panel pad" style="overflow:auto"><table><thead><tr>'
      +'<th>verdict · fact</th><th>subject</th><th>E</th><th>L · layer</th><th>ns</th><th>tag</th>'
      +'</tr></thead><tbody>'+body+'</tbody></table></div>';
    $("#fcount",m).textContent=rows.length+" / "+fs.length;
    ["fv","fe","ft","fq"].forEach(function(id){
      var e=$("#"+id,m);var ev=id==="fq"?"input":"change";
      e.addEventListener(ev,function(){STATE[id]=e.value;var pos=e.selectionStart;renderInto();if(id==="fq"){var n=$("#fq");n.focus();try{n.setSelectionRange(pos,pos);}catch(_){}}});
    });
    Array.prototype.forEach.call(m.querySelectorAll("tbody tr[data-id]"),function(tr){
      tr.onclick=function(){var id=tr.getAttribute("data-id");STATE.open[id]=!STATE.open[id];renderInto();};
    });
  }

  function renderMatrix(m){
    var mat=DATA.verdict_matrix||{}, E=["E0","E1","E2","E3","E4"];
    var verds=Object.keys(mat).sort(function(a,b){return (b==="(none)")-(a==="(none)");});
    var max=0;Object.keys(mat).forEach(function(v){E.forEach(function(e){max=Math.max(max,mat[v][e]||0);});});
    function shade(n){if(!n)return "";var t=0.18+0.82*(n/max);return "background:color-mix(in srgb,var(--accent) "+Math.round(t*100)+"%, var(--surface))";}
    var colTot={};E.forEach(function(e){colTot[e]=0;});
    var body=verds.map(function(v){
      var rowTot=0;
      var cells=E.map(function(e){var n=mat[v][e]||0;rowTot+=n;colTot[e]+=n;
        return '<td><div class="cell'+(n?"":" zero")+'" style="'+shade(n)+'" data-tip="'+esc(v)+' · '+e+' ('+EMEAN[e]+'): '+n+' fact'+(n===1?"":"s")+'">'+n+'</div></td>';}).join("");
      return '<tr><td class="rowh">'+pill(v==="(none)"?null:v)+'</td>'+cells+'<td class="tot">'+rowTot+'</td></tr>';
    }).join("");
    var foot='<tr><td class="rowh muted">total</td>'+E.map(function(e){return '<td class="tot">'+colTot[e]+'</td>';}).join("")+'<td class="tot">'+facts().length+'</td></tr>';
    var ramp='<div class="ramp"><span>fewer</span><span class="bar">'+[0.18,0.4,0.6,0.8,1].map(function(t){return '<i style="background:color-mix(in srgb,var(--accent) '+Math.round(t*100)+'%,var(--surface))"></i>';}).join("")+'</span><span>more facts</span></div>';
    m.innerHTML='<div class="panel pad" style="overflow:auto"><table class="matrix"><thead><tr><th></th>'
      +E.map(function(e){return '<th>'+e+'<div class="muted" style="font-weight:400">'+EMEAN[e]+'</div></th>';}).join("")+'<th>Σ</th></tr></thead>'
      +'<tbody>'+body+foot+'</tbody></table>'+ramp+'</div>';
    bindTips(m);
  }

  function renderProv(m){
    var counts={};facts().forEach(function(f){(f.assumptions||[]).forEach(function(a){counts[a]=(counts[a]||0)+1;});});
    var asms=Object.keys(counts).sort(function(a,b){return counts[b]-counts[a]||a.localeCompare(b);});
    if(STATE.asm==null&&asms.length)STATE.asm=DATA.invalidation_demo&&DATA.invalidation_demo.assumption&&counts[DATA.invalidation_demo.assumption]?DATA.invalidation_demo.assumption:asms[0];
    var demo=DATA.invalidation_demo||{};
    var callout='<div class="callout">Invalidating <b class="mono">'+esc(demo.assumption)+'</b> downgrades <b>'+((demo.downgraded_facts||[]).length)+'</b> dependent fact'+((demo.downgraded_facts||[]).length===1?"":"s")+' via the store’s invalidation traversal — appended as a downgrade record, never deleted.</div>';
    var list=asms.map(function(a){return '<button data-a="'+esc(a)+'" aria-current="'+(STATE.asm===a)+'"><span>'+esc(a)+'</span><span class="c">'+counts[a]+'</span></button>';}).join("");
    var carried=facts().filter(function(f){return (f.assumptions||[]).indexOf(STATE.asm)>=0;});
    var dg=(demo.downgraded_facts||[]);
    var rowsH=carried.map(function(f){
      var down=dg.indexOf(f.fact_id)>=0;
      return '<tr class="'+f.analyzer.tag.toLowerCase()+'"><td>'+pill(f.verdict)+(down?' <span class="tag heuristic">would downgrade</span>':"")+'<div class="fid mono">'+esc(f.fact_id)+'</div></td>'
        +'<td class="mono">'+esc(f.content.subject||"")+'</td><td>'+ebadge(f.evidence_level)+'</td></tr>';
    }).join("");
    m.innerHTML=callout+'<div class="prov"><div class="panel pad"><div class="cap" style="font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-faint);margin-bottom:8px">assumptions ('+asms.length+')</div><div class="asmlist">'+list+'</div></div>'
      +'<div class="panel pad" style="overflow:auto"><div class="muted" style="margin-bottom:10px">Facts resting on <b class="mono" style="color:var(--ink)">'+esc(STATE.asm)+'</b> — <b>'+carried.length+'</b></div>'
      +'<table><thead><tr><th>verdict · fact</th><th>subject</th><th>E</th></tr></thead><tbody>'+rowsH+'</tbody></table></div></div>';
    Array.prototype.forEach.call(m.querySelectorAll(".asmlist button"),function(b){b.onclick=function(){STATE.asm=b.getAttribute("data-a");renderInto();};});
  }

  function renderLattice(m){
    var L=DATA.candidate_lattice;
    if(!L){m.innerHTML='<div class="panel pad muted">No candidate lattice in this bundle.</div>';return;}
    var fam=(L.compatible_families||[]).map(function(f){return '<span class="chip" style="color:var(--ink)">'+esc(f)+'</span>';}).join(" ");
    var obl=(L.test_obligations||[]).map(function(o){return '<tr><td class="mono">'+esc(o.intervention)+'</td><td class="mono muted">'+esc((o.separates||[]).join(", "))+'</td></tr>';}).join("");
    m.innerHTML='<div class="grid" style="grid-template-columns:1fr 1fr">'
      +'<div class="panel pad"><div class="cap" style="font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-faint)">equivalence class '+esc(L.equivalence_class)+'</div>'
      +'<div style="margin:12px 0">'+pill(L.verdict)+'</div>'
      +'<div class="muted" style="font-size:13px">Compatible grammar families, retained in parallel (neither eliminated until an intervention separates them):</div>'
      +'<div style="margin-top:10px">'+fam+'</div></div>'
      +'<div class="panel pad"><div class="cap" style="font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-faint)">test obligations</div>'
      +'<div class="muted" style="font-size:13px;margin:8px 0">The interventions that would discriminate the members:</div>'
      +'<table><thead><tr><th>intervention</th><th>separates</th></tr></thead><tbody>'+obl+'</tbody></table></div></div>';
  }

  function renderDiff(m){
    var d=DATA.cross_domain_diff;
    if(!d){m.innerHTML='<div class="panel pad muted">No cross-domain diff in this bundle.</div>';return;}
    var motifs=(d.shared_motifs||[]).map(function(x){return '<span class="m shared">'+esc(x)+'</span>';}).join("")
      +(d.divergent||[]).map(function(x){return '<span class="m diverge">'+esc(x)+' ✕</span>';}).join("");
    var app=(d.apparatus_differences||[]).map(function(a){return '<tr><td class="mono">'+esc(a.key)+'</td><td class="mono muted">'+esc(a.a)+'</td><td class="mono muted">'+esc(a.b)+'</td></tr>';}).join("");
    m.innerHTML='<div class="gauges">'
      +'<div class="panel gauge"><div class="v">'+d.similarity.toFixed(2)+'</div><div class="l">similarity</div><div class="track"><i style="width:'+(d.similarity*100)+'%"></i></div></div>'
      +'<div class="panel gauge"><div class="v">'+d.confidence.toFixed(2)+'</div><div class="l">confidence</div><div class="track"><i style="width:'+(d.confidence*100)+'%"></i></div></div></div>'
      +'<div class="panel pad" style="margin-bottom:16px"><span class="muted">correlator</span> <span class="chip" style="color:var(--ink)">'+esc(d.correlator)+'</span>'
      +'<div class="muted" style="font-size:12.5px;margin-top:10px">'+esc(d.ontology_claim)+'</div>'
      +'<div class="motifs">'+motifs+'</div></div>'
      +'<div class="grid" style="grid-template-columns:1fr 1fr">'
      +'<div class="panel pad"><div class="cap" style="font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-faint)">apparatus differences</div>'
      +'<table style="margin-top:10px"><thead><tr><th></th><th>A</th><th>B</th></tr></thead><tbody>'+app+'</tbody></table></div>'
      +'<div class="panel pad"><div class="cap" style="font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-faint)">least-cost discriminator</div>'
      +'<div style="margin-top:12px"><span class="chip" style="color:var(--accent);border-color:var(--accent)">'+esc(d.least_cost_discriminator||"none")+'</span></div>'
      +'<div class="muted" style="font-size:12.5px;margin-top:8px">The cheapest admissible intervention that still separates the domains.</div></div></div>';
  }

  function renderGraph(m){
    var g=DATA.structural_graph;
    if(!g||!g.nodes.length){m.innerHTML='<div class="panel pad muted">No structural graph in this bundle.</div>';return;}
    var nodes=g.nodes.slice().sort(function(a,b){return (a.order||0)-(b.order||0);});
    var W=Math.max(560,nodes.length*180), H=260, pad=90;
    var xs={};nodes.forEach(function(n,i){xs[n.id]=pad+i*((W-2*pad)/Math.max(1,nodes.length-1));});
    var y=H/2;
    var edges=(g.edges||[]).map(function(e){
      var x1=xs[e.from],x2=xs[e.to];if(x1==null||x2==null)return "";
      if(e.kind==="time")return '<line x1="'+x1+'" y1="'+y+'" x2="'+x2+'" y2="'+y+'" stroke="var(--accent)" stroke-width="2" marker-end="url(#arw)"/>';
      var my=y+70, mx=(x1+x2)/2;
      return '<path d="M'+x1+' '+(y+16)+' Q '+mx+' '+my+' '+x2+' '+(y+16)+'" fill="none" stroke="var(--ink-faint)" stroke-width="1.5" stroke-dasharray="4 4"/>'
        +'<text x="'+mx+'" y="'+(my+2)+'" text-anchor="middle" fill="var(--ink-faint)" font-size="10" font-family="var(--mono)">'+esc(e.via||"")+'</text>';
    }).join("");
    var ns=nodes.map(function(n){var x=xs[n.id];
      return '<g><circle cx="'+x+'" cy="'+y+'" r="26" fill="var(--surface2)" stroke="var(--accent)" stroke-width="2"/>'
        +'<text x="'+x+'" y="'+(y+4)+'" text-anchor="middle" fill="var(--ink)" font-size="11" font-family="var(--mono)" font-weight="700">'+esc(n.op)+'</text>'
        +'<text x="'+x+'" y="'+(y+46)+'" text-anchor="middle" fill="var(--ink-faint)" font-size="10" font-family="var(--mono)">'+esc((n.ports||[]).join(","))+'</text></g>';
    }).join("");
    m.innerHTML='<div class="panel pad" style="overflow:auto"><svg viewBox="0 0 '+W+' '+H+'" role="img" aria-label="B9 act-trace structural graph">'
      +'<defs><marker id="arw" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0 0 L7 3 L0 6 z" fill="var(--accent)"/></marker></defs>'
      +edges+ns+'</svg>'
      +'<div class="muted" style="font-size:12.5px;margin-top:6px"><span style="color:var(--accent)">━</span> time ordering &nbsp; <span style="color:var(--ink-faint)">┈</span> shared coordinate</div></div>';
  }

  // ---- tooltip / theme / boot ------------------------------------------
  function bindTips(root){
    var tip=$("#tip");
    Array.prototype.forEach.call(root.querySelectorAll("[data-tip]"),function(n){
      n.addEventListener("mousemove",function(ev){tip.textContent=n.getAttribute("data-tip");tip.style.opacity="1";
        tip.style.left=Math.min(ev.clientX+14,innerWidth-260)+"px";tip.style.top=(ev.clientY+14)+"px";});
      n.addEventListener("mouseleave",function(){tip.style.opacity="0";});
    });
  }
  function toggleTheme(){
    var cur=document.documentElement.getAttribute("data-theme");
    var next=cur==="dark"?"light":(cur==="light"?"dark":(matchMedia("(prefers-color-scheme: dark)").matches?"light":"dark"));
    document.documentElement.setAttribute("data-theme",next);
  }
  function renderInto(){
    var main=$("#main"), s=SURFACES.filter(function(x){return x.id===STATE.s;})[0]||SURFACES[0];
    main.innerHTML=summaryStrip()+'<div class="surface-head"><h2>'+esc(s.name)+'</h2><p>'+esc(s.desc)+'</p></div><div id="body"></div>';
    s.fn($("#body",main));
  }
  function render(){
    Array.prototype.forEach.call(document.querySelectorAll("#nav button"),function(b){
      b.setAttribute("aria-current",b.getAttribute("data-s")===STATE.s);});
    renderInto();
  }
  buildRail();
  var h=(location.hash||"").replace("#","");
  if(SURFACES.some(function(s){return s.id===h;}))STATE.s=h;
  render();
})();
</script>
"""


def render_html(bundle=None) -> str:
    """Return the self-contained workbench HTML with the bundle inlined."""
    bundle = bundle if bundle is not None else build_bundle()
    data = json.dumps(bundle, separators=(",", ":")).replace("</", "<\\/")
    return PAGE.replace("__PIR_DATA__", data)


def main() -> int:
    bundle = build_bundle()
    html = render_html(bundle)
    out_dir = os.path.join(ROOT, "build", "pir_view")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "workbench.html")
    with open(path, "w") as f:
        f.write(html)
    print(f"PIR workbench built: {path}  ({len(html)//1024} KB)")
    print(f"  {bundle['meta']['n_facts']} facts · {bundle['meta']['n_benchmarks']} benchmarks · 6 surfaces")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
