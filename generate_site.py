"""Build the single-file HTML case study from generated JSON artifacts."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "research.json"
VERIFY = ROOT / "data" / "verification.json"
OUT = ROOT / "site" / "index.html"


def main():
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    verification = json.loads(VERIFY.read_text(encoding="utf-8"))
    data_js = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    verify_js = json.dumps(verification, ensure_ascii=False).replace("</", "<\\/")
    html = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Raghav Kathuria | Composio Toolkit Readiness</title>
  <style>
    :root {{
      --ink: #101a2b; --muted: #6c7890; --paper: #f7f9fc; --card: #ffffff;
      --line: #e2e8f0; --lime: #c8f169; --blue: #3a5cff; --violet: #7058e8;
      --orange: #f59e0b; --red: #ef5b68; --green: #1ca77a; --shadow: 0 18px 60px rgba(16,26,43,.09);
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; color: var(--ink); background: var(--paper); font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif; line-height: 1.45; }}
    a {{ color: inherit; }}
    .shell {{ max-width: 1420px; margin: 0 auto; padding: 30px 26px 80px; }}
    .eyebrow {{ color: var(--blue); font-size: 12px; font-weight: 800; letter-spacing: .16em; text-transform: uppercase; }}
    .topline {{ display:flex; justify-content:space-between; align-items:center; gap:18px; margin-bottom:55px; flex-wrap:wrap; }}
    .brand {{ font-weight: 900; letter-spacing: -.04em; font-size: 17px; }}
    .stamp {{ color: var(--muted); font-size: 12px; }}
    .topnav {{ display:flex; align-items:center; gap:14px; font-size:12px; font-weight:800; color:var(--muted); }}
    .topnav a {{ text-decoration:none; }} .topnav a:hover {{ color:var(--blue); }}
    .ready {{ color:#087a59; background:#dff8ee; border:1px solid #b6edd9; border-radius:999px; padding:6px 9px; font-size:10px; letter-spacing:.08em; }}
    .hero {{ display:grid; grid-template-columns: minmax(0, 1.3fr) minmax(310px, .7fr); gap: 50px; align-items:end; padding-bottom: 45px; border-bottom: 1px solid var(--line); }}
    h1 {{ max-width: 850px; margin: 12px 0 18px; font-size: clamp(42px, 6vw, 82px); line-height: .96; letter-spacing: -.07em; }}
    .hero p {{ max-width: 760px; color: #46536a; font-size: 18px; margin: 0; }}
    .hero-actions {{ display:flex; gap:10px; flex-wrap:wrap; margin-top:24px; }}
    .button {{ display:inline-flex; align-items:center; gap:8px; border-radius:12px; padding:11px 14px; background:var(--ink); color:white; text-decoration:none; font-size:12px; font-weight:800; }}
    .button.secondary {{ background:white; color:var(--ink); border:1px solid var(--line); }}
    .signal {{ background: var(--ink); color: white; border-radius: 24px; padding: 26px; box-shadow: var(--shadow); position:relative; overflow:hidden; }}
    .signal:after {{ content:""; width:150px; height:150px; border:1px solid rgba(200,241,105,.4); border-radius:50%; position:absolute; right:-54px; top:-50px; }}
    .signal strong {{ display:block; font-size: 25px; line-height:1.08; letter-spacing:-.04em; margin: 8px 0 14px; position:relative; z-index:1; }}
    .signal small {{ color:#b9c3d4; position:relative; z-index:1; }}
    .accent {{ color: var(--lime); }}
    .kpis {{ display:grid; grid-template-columns: repeat(6, 1fr); gap: 12px; margin: 26px 0 54px; }}
    .kpi {{ background:var(--card); border:1px solid var(--line); border-radius:18px; padding:18px; min-height:115px; }}
    .kpi b {{ display:block; font-size:31px; line-height:1; letter-spacing:-.05em; margin-bottom:8px; }}
    .kpi span {{ display:block; color:var(--muted); font-size:12px; font-weight:700; }}
    .section {{ margin-top: 58px; }}
    .section-head {{ display:flex; justify-content:space-between; align-items:end; gap:20px; margin-bottom:18px; }}
    h2 {{ margin:0; font-size:30px; letter-spacing:-.05em; }}
    h3 {{ margin:0 0 8px; font-size:18px; letter-spacing:-.03em; }}
    .lede {{ color:var(--muted); max-width: 720px; margin: 6px 0 0; }}
    .insights {{ display:grid; grid-template-columns: repeat(3, 1fr); gap:14px; }}
    .insight {{ background:var(--card); border:1px solid var(--line); border-radius:20px; padding:23px; }}
    .insight .num {{ color:var(--blue); font-size:12px; font-weight:900; letter-spacing:.12em; }}
    .insight p {{ color:#566278; margin:8px 0 0; font-size:14px; }}
    .decision-grid {{ display:grid; grid-template-columns:repeat(3,1fr); gap:14px; }}
    .decision-col {{ border-radius:20px; padding:22px; border:1px solid var(--line); background:var(--card); min-height:185px; }}
    .decision-col.build {{ border-top:4px solid var(--green); }} .decision-col.validate {{ border-top:4px solid var(--orange); }} .decision-col.outreach {{ border-top:4px solid var(--red); }}
    .decision-col .big {{ display:block; font-size:42px; line-height:1; letter-spacing:-.06em; margin:16px 0 6px; }}
    .decision-col p {{ color:var(--muted); font-size:13px; margin:0; }}
    .category-grid {{ display:grid; grid-template-columns:repeat(5,1fr); gap:10px; margin-top:14px; }}
    .category-card {{ background:var(--card); border:1px solid var(--line); border-radius:15px; padding:14px; }}
    .category-card strong {{ display:block; font-size:13px; line-height:1.2; min-height:34px; }}
    .category-card small {{ color:var(--muted); font-size:11px; }}
    .mini-bar {{ display:flex; height:7px; border-radius:99px; overflow:hidden; background:#edf1f6; margin-top:12px; }}
    .mini-bar i {{ display:block; height:100%; }}
    .flow {{ display:grid; grid-template-columns:repeat(4,1fr); gap:0; background:var(--ink); border-radius:24px; overflow:hidden; color:white; }}
    .step {{ padding:24px 20px; border-right:1px solid rgba(255,255,255,.12); min-height:150px; }}
    .step:last-child {{ border-right:0; }}
    .step .index {{ color:var(--lime); font-weight:900; font-size:12px; }}
    .step h3 {{ margin-top:22px; }}
    .step p {{ color:#b8c4d5; font-size:13px; margin:0; }}
    .proof {{ display:grid; grid-template-columns: 1fr 1fr; gap:14px; }}
    .panel {{ background:var(--card); border:1px solid var(--line); border-radius:20px; padding:24px; }}
    .panel p {{ color:#566278; font-size:14px; }}
    .metric-line {{ display:flex; justify-content:space-between; gap:12px; padding:11px 0; border-bottom:1px solid var(--line); font-size:14px; }}
    .metric-line:last-child {{ border-bottom:0; }}
    .metric-line b {{ color:var(--ink); }}
    .bar {{ height:8px; background:#edf1f6; border-radius:99px; overflow:hidden; margin-top:14px; }}
    .bar i {{ display:block; height:100%; background:var(--blue); border-radius:99px; }}
    .filters {{ display:flex; flex-wrap:wrap; gap:10px; margin:15px 0 14px; }}
    input, select {{ appearance:none; background:white; border:1px solid var(--line); border-radius:12px; padding:11px 13px; color:var(--ink); font:inherit; font-size:13px; }}
    input {{ min-width:270px; flex:1; }}
    .table-wrap {{ overflow:auto; border:1px solid var(--line); border-radius:20px; background:white; box-shadow:var(--shadow); }}
    table {{ width:100%; border-collapse:collapse; min-width:1260px; font-size:12px; }}
    th {{ background:#f1f4f8; color:#68758b; font-size:10px; letter-spacing:.08em; text-transform:uppercase; text-align:left; padding:13px 12px; position:sticky; top:0; z-index:1; }}
    td {{ padding:14px 12px; vertical-align:top; border-top:1px solid #eef2f6; max-width:260px; }}
    tr:hover td {{ background:#fbfcfe; }}
    .app {{ font-weight:850; white-space:nowrap; }}
    .sub {{ color:var(--muted); font-size:11px; margin-top:3px; }}
    .pill {{ display:inline-flex; padding:4px 8px; border-radius:999px; font-size:10px; font-weight:800; white-space:nowrap; }}
    .green {{ color:#087a59; background:#dff8ee; }} .amber {{ color:#9a5b00; background:#fff0c9; }}
    .red {{ color:#a43a45; background:#ffe0e3; }} .blue {{ color:#2846bf; background:#e4eaff; }}
    .purple {{ color:#5944b7; background:#ece8ff; }}
    .source {{ color:var(--blue); text-decoration:none; font-weight:750; }}
    .source:hover {{ text-decoration:underline; }}
    .verification-grid {{ display:grid; grid-template-columns: 1fr 1.5fr; gap:14px; }}
    .score {{ display:flex; align-items:baseline; gap:10px; }}
    .score b {{ font-size:50px; line-height:1; letter-spacing:-.06em; }}
    .score span {{ color:var(--muted); font-size:13px; }}
    .checklist {{ display:grid; grid-template-columns:repeat(3,1fr); gap:9px; margin-top:16px; }}
    .check {{ border:1px solid var(--line); border-radius:12px; padding:12px; font-size:12px; }}
    .check strong {{ display:block; font-size:16px; margin-bottom:2px; }}
    .check em {{ color:var(--muted); font-style:normal; }}
    .check a {{ display:inline-block; color:var(--blue); font-size:11px; font-weight:800; margin-top:8px; text-decoration:none; }}
    .check a:hover {{ text-decoration:underline; }}
    .check p {{ color:#566278; font-size:11px; margin:7px 0 0; line-height:1.35; }}
    .limitations {{ color:#59667d; font-size:13px; margin:0; padding-left:17px; }}
    .footer {{ display:flex; justify-content:space-between; gap:20px; color:var(--muted); font-size:12px; border-top:1px solid var(--line); padding-top:22px; margin-top:60px; }}
    @media (max-width: 1100px) {{ .kpis {{grid-template-columns:repeat(3,1fr);}} .category-grid {{grid-template-columns:repeat(3,1fr);}} }}
    @media (max-width: 900px) {{ .hero,.proof,.verification-grid {{grid-template-columns:1fr;}} .kpis {{grid-template-columns:repeat(2,1fr);}} .insights,.flow,.decision-grid {{grid-template-columns:1fr;}} .category-grid {{grid-template-columns:repeat(2,1fr);}} .step {{border-right:0;border-bottom:1px solid rgba(255,255,255,.12);}} .step:last-child {{border-bottom:0;}} }}
    @media (max-width: 560px) {{ .shell {{padding:22px 15px 60px;}} h1 {{font-size:46px;}} .kpis {{grid-template-columns:1fr 1fr;}} .topline {{margin-bottom:32px;}} }}
  </style>
</head>
<body>
  <main class="shell">
    <div class="topline"><div class="brand">COMPOSIO / TOOLKIT READINESS</div><nav class="topnav"><a href="#queue">Queue</a><a href="#matrix">Matrix</a><a href="#verification">Verification</a><span class="ready">READY TO DEPLOY</span></nav><div class="stamp">AI Product Ops Intern · Raghav Kathuria · 16 Jul 2026</div></div>
    <section class="hero">
      <div><div class="eyebrow">100-app research sprint</div><h1>Access is the bottleneck, <span class="accent">not the API surface.</span></h1><p>Most of this set exposes a workable REST, GraphQL or CLI surface. The hard part of turning an app into an agent toolkit is getting the right credentials through reviews, admin controls, paid tiers and compliance gates.</p><div class="hero-actions"><a class="button" href="#matrix">Jump to evidence matrix ↓</a><a class="button secondary" href="#verification">See verification ↓</a></div></div>
      <aside class="signal"><div class="eyebrow accent">Executive signal</div><strong>Prioritize the easy wins. Route the gated tail to partnerships.</strong><small>Read the matrix as a sourcing queue, not a directory.</small></aside>
    </section>

    <section class="kpis" id="kpis"></section>

    <section class="section"><div class="section-head"><div><div class="eyebrow">01 / what changed my mind</div><h2>Three patterns worth acting on</h2></div><p class="lede">The 100 rows are useful only when they change what the team does next.</p></div>
      <div class="insights">
        <article class="insight"><div class="num">01 — BUILDABILITY</div><h3>Public docs are not the same as installability.</h3><p>API breadth is usually available. Credential acquisition, tenant install and production review determine whether a toolkit can ship quickly.</p></article>
        <article class="insight"><div class="num">02 — EASY WINS</div><h3>Developer infra and productivity are the cleanest queue.</h3><p>Self-serve tokens, strong docs and broad CRUD/webhook surfaces make GitHub, Vercel, Notion, Linear, Asana and similar apps high-leverage starts.</p></article>
        <article class="insight"><div class="num">03 — OUTREACH</div><h3>Fintech, ads and media-native products need a different motion.</h3><p>Sandbox, app-review, business-verification and sales-led access recur. An agent can flag the blocker; it cannot replace the relationship.</p></article>
      </div>
    </section>

    <section class="section" id="queue"><div class="section-head"><div><div class="eyebrow">02 / sourcing view</div><h2>Translate research into a queue</h2></div><p class="lede">Every row should create a next action: build, validate, or route to outreach.</p></div>
      <div class="decision-grid" id="decisionBoard"></div><div class="category-grid" id="categoryGrid"></div>
    </section>

    <section class="section"><div class="section-head"><div><div class="eyebrow">03 / the agent</div><h2>Research loop</h2></div><p class="lede">A deterministic pipeline keeps the work reproducible and makes uncertainty visible.</p></div>
      <div class="flow"><div class="step"><div class="index">01 / PLAN</div><h3>Seed & route</h3><p>Normalize the assignment list into categories, source hints and a review queue.</p></div><div class="step"><div class="index">02 / RESEARCH</div><h3>Classify</h3><p>Combine source URL, category baseline and targeted overrides into auth, access, API and verdict fields.</p></div><div class="step"><div class="index">03 / VERIFY</div><h3>Cross-check</h3><p>Run a stratified 12-row sample against real documentation signals and keep first-pass deltas.</p></div><div class="step"><div class="index">04 / HAND OFF</div><h3>Queue humans</h3><p>Expose low-confidence rows, partner gates and product/API ambiguity as the next action.</p></div></div>
    </section>

    <section class="section"><div class="section-head"><div><div class="eyebrow">04 / proof</div><h2>What was actually built</h2></div></div>
      <div class="proof"><article class="panel"><h3>Runnable trigger</h3><p>This page is generated from the same dataset the agent writes. From the repository root:</p><pre style="background:#101a2b;color:#dce6f4;border-radius:14px;padding:16px;overflow:auto;font-size:12px">python research_agent.py
python verify.py
python generate_site.py
python -m http.server 8000</pre><p style="margin-bottom:0">Then open <b>site/index.html</b> or <b>http://localhost:8000/site/</b>. <code>--live-check</code> optionally probes evidence URLs without treating failure as a negative finding.</p></article><article class="panel"><h3>Where a human is still needed</h3><p>The pipeline is deliberately honest about its boundary: URL reachability is not credential proof, and product landing pages are not contract terms. Rows marked for follow-up need a direct docs read, a trial/sandbox check, or a partnership conversation.</p><div class="metric-line"><span>Explicit MCP hints in seed list</span><b id="mcpCount">—</b></div><div class="metric-line"><span>Rows queued for human follow-up</span><b id="followUp">—</b></div><div class="metric-line"><span>Provided parity signal used</span><b>top-demand names tagged</b></div></article></div>
    </section>

    <section class="section" id="matrix"><div class="section-head"><div><div class="eyebrow">05 / the evidence matrix</div><h2>100 apps, one sourcing queue</h2></div><p class="lede">Search, filter, and open the cited evidence. “Medium” means the seed hint is useful but not a full contract-level audit.</p></div>
      <div class="filters"><input id="search" placeholder="Search app, category or blocker…" /><select id="category"><option value="">All categories</option></select><select id="access"><option value="">All access signals</option><option value="self">Self-serve signal</option><option value="gate">Gate / review / paid</option><option value="outreach">Outreach first</option></select></div>
      <div class="table-wrap"><table><thead><tr><th>#</th><th>App</th><th>Auth</th><th>Access</th><th>API surface</th><th>MCP signal</th><th>Verdict</th><th>Evidence</th></tr></thead><tbody id="rows"></tbody></table></div>
    </section>

    <section class="section" id="verification"><div class="section-head"><div><div class="eyebrow">06 / verification</div><h2>First pass → reviewed pass</h2></div><p class="lede">This is a directional quality check, not a claim that 12 rows statistically prove the other 88.</p></div>
      <div class="verification-grid"><article class="panel"><div class="score"><b id="firstScore">—</b><span>first-pass field accuracy<br/>on the 12-row sample</span></div><div class="bar"><i id="firstBar" style="width:0%"></i></div><div class="score" style="margin-top:24px"><b id="finalScore">—</b><span>after human + source loop</span></div><div class="bar"><i id="finalBar" style="width:0%;background:var(--green)"></i></div><p style="margin-bottom:0">12 official source pages were manually checked. The corrections are visible in the sample cards; this is evidence of the loop, not proof that the other 88 rows are done.</p></article><article class="panel"><h3>Spot-check sample</h3><div class="checklist" id="checks"></div></article></div>
    </section>

    <section class="section"><div class="section-head"><div><div class="eyebrow">07 / limits</div><h2>What I would do next</h2></div></div><div class="panel"><ul class="limitations"><li>Turn medium-confidence rows into browser-assisted doc checks before any production toolkit is sourced.</li><li>Use Composio/MCP credentials only after the access gate is verified; the current artifact needs no secrets to run.</li><li>Separate “has an API” from “can be distributed as an agent toolkit” in the sourcing rubric.</li><li>Re-run the live probe and spot-check before submission because API policies, plan gates and MCP availability drift.</li></ul></div></section>

    <div class="footer"><span>Built as a single self-explanatory HTML case study.</span><span>Source: supplied assignment brief + supplied Composio parity snapshot.</span></div>
  </main>
  <script>
    const PAYLOAD = {data_js};
    const VERIFY = {verify_js};
    const rows = PAYLOAD.rows;
    const $ = (id) => document.getElementById(id);
    const esc = (s) => String(s ?? '').replace(/[&<>"']/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]));
    const pct = (value) => Math.round(value * 100) + '%';
    const isGate = (row) => /review|admin|paid|compliance|partner|gated|verification|sales-led|not self-serve/i.test(row.access);
    const isOutreach = (row) => /outreach first/i.test(row.verdict);
    const isSelf = (row) => /self-serve|self-hostable/i.test(row.access) && !isGate(row);
    const pill = (text, kind) => `<span class="pill ${{kind}}">${{esc(text)}}</span>`;
    const verdictKind = (text) => /outreach/i.test(text) ? 'red' : /gate|validation|review/i.test(text) ? 'amber' : 'green';
    const categories = [...new Set(rows.map(r => r.category))];
    categories.forEach(c => $('category').insertAdjacentHTML('beforeend', `<option value="${{esc(c)}}">${{esc(c)}}</option>`));
    const highDemand = rows.filter(r => r.composio_demand_rank).length;
    const explicitMcp = rows.filter(r => /explicit mcp/i.test(r.mcp)).length;
    const evidenceCount = rows.filter(r => r.evidence).length;
    $('kpis').innerHTML = [
      ['100','apps mapped','green'], ['10','categories','blue'], [String(evidenceCount),'seed evidence URLs','purple'], [String(highDemand),'parity demand signals','amber'], [String(rows.filter(r => !r.human_follow_up).length),'targeted profiles','blue'], [String(explicitMcp),'explicit MCP hints','green']
    ].map(([v,l,k]) => `<div class="kpi"><b>${{v}}</b><span>${{l}}</span></div>`).join('');
    $('mcpCount').textContent = explicitMcp + ' / 100';
    $('followUp').textContent = rows.filter(r => r.human_follow_up).length + ' / 100';

    const queueOf = (row) => isOutreach(row) ? 'outreach' : isGate(row) ? 'validate' : 'build';
    const queueCopy = {{build:['Build now','Self-serve signal with a usable documented surface.','Start with the highest-demand names here.'], validate:['Validate first','API exists, but scopes, review, paid tier or admin setup can slow shipping.','Browser-check the access path before sourcing.'], outreach:['Route to outreach','Commercial or product/API ambiguity is the blocker.','Do not burn toolkit build time before access is clear.']}};
    const queueCounts = Object.fromEntries(Object.keys(queueCopy).map(k => [k, rows.filter(r => queueOf(r) === k).length]));
    $('decisionBoard').innerHTML = Object.entries(queueCopy).map(([key, value]) => `<article class="decision-col ${{key}}"><div class="eyebrow">${{value[0]}}</div><span class="big">${{queueCounts[key]}}</span><p><b>${{value[1]}}</b><br/>${{value[2]}}</p></article>`).join('');
    const byCategory = categories.map(category => {{
      const subset = rows.filter(r => r.category === category); const counts = {{build:subset.filter(r => queueOf(r)==='build').length,validate:subset.filter(r => queueOf(r)==='validate').length,outreach:subset.filter(r => queueOf(r)==='outreach').length}};
      return `<article class="category-card"><strong>${{esc(category)}}</strong><small>${{counts.build}} build · ${{counts.validate}} validate · ${{counts.outreach}} outreach</small><div class="mini-bar"><i style="width:${{counts.build*10}}%;background:var(--green)"></i><i style="width:${{counts.validate*10}}%;background:var(--orange)"></i><i style="width:${{counts.outreach*10}}%;background:var(--red)"></i></div></article>`;
    }});
    $('categoryGrid').innerHTML = byCategory.join('');

    function render() {{
      const q = $('search').value.toLowerCase().trim(); const cat = $('category').value; const access = $('access').value;
      const filtered = rows.filter(r => {{
        const blob = [r.app,r.category,r.auth,r.access,r.api,r.verdict].join(' ').toLowerCase();
        return (!q || blob.includes(q)) && (!cat || r.category === cat) && (!access || (access === 'self' && isSelf(r)) || (access === 'gate' && isGate(r)) || (access === 'outreach' && isOutreach(r)));
      }});
      $('rows').innerHTML = filtered.map(r => {{
        const demand = r.composio_demand_rank ? `<div class="sub">Composio demand #${{r.composio_demand_rank}}</div>` : '';
        const evidence = r.evidence ? `<a class="source" href="${{esc(r.evidence)}}" target="_blank" rel="noreferrer">open source ↗</a><div class="sub">${{esc(r.evidence_grade)}} confidence</div>` : '<span class="sub">No URL in seed hint</span>';
        const mcp = /explicit mcp/i.test(r.mcp) ? pill('explicit', 'purple') : pill('not in seed', 'blue');
        return `<tr><td>${{r.id}}</td><td><div class="app">${{esc(r.app)}}</div><div class="sub">${{esc(r.category)}}</div>${{demand}}</td><td>${{esc(r.auth)}}</td><td>${{esc(r.access)}}</td><td>${{esc(r.api)}}</td><td>${{mcp}}<div class="sub">${{esc(r.mcp)}}</div></td><td>${{pill(r.verdict, verdictKind(r.verdict))}}</td><td>${{evidence}}</td></tr>`;
      }}).join('');
    }}
    ['search','category','access'].forEach(id => $(id).addEventListener('input', render));
    render();
    $('firstScore').textContent = pct(VERIFY.first_pass.accuracy); $('firstBar').style.width = pct(VERIFY.first_pass.accuracy);
    $('finalScore').textContent = pct(VERIFY.after_human_and_source_loop.accuracy); $('finalBar').style.width = pct(VERIFY.after_human_and_source_loop.accuracy);
    $('checks').innerHTML = VERIFY.records.map(r => `<div class="check"><strong>${{esc(r.app)}}</strong><em>${{r.corrected_fields.length ? 'corrected: ' + r.corrected_fields.join(', ') : 'no field delta'}}</em><a href="${{esc(r.source_url)}}" target="_blank" rel="noreferrer">official source ↗</a><p>${{esc(r.review_note)}}</p></div>`).join('');
  </script>
</body>
</html>'''
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"Wrote {OUT} ({len(html):,} bytes)")


if __name__ == "__main__":
    main()
