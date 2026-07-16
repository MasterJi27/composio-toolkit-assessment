# Composio Product Research Platform

**Deterministic research pipeline with a 20-app verification sample.** — researches 100 SaaS products, determines toolkit buildability, generates verified outputs with confidence scores, and produces an interactive HTML case study.

Built by **Raghav Kathuria**.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Supervisor Agent                            │
│  Queue · Scheduling · Retries · Checkpoint Recovery · Orchestration │
└─────────────────────────────────────────────────────────────────────┘
         │
    ┌────┴────────────────────────────────────────────────────┐
    ▼                                                         ▼
┌─────────────┐  ┌──────────────┐  ┌────────────────┐  ┌──────────────┐
│  Research   │  │   Evidence   │  │  Verification  │  │  Confidence  │
│  Agent      │─▶│   Agent      │─▶│   Agent        │─▶│   Agent      │
│  (100 apps) │  │  (sources)   │  │  (20-sample)   │  │  (HIGH/MED/) │
└─────────────┘  └──────────────┘  └────────────────┘  └──────────────┘
                                                              │
                                                              ▼
                                                     ┌──────────────┐
                                                     │  Human       │
                                                     │  Review Queue│
                                                     │  (only when   │
                                                     │   needed)    │
                                                     └──────────────┘
                                                              │
                                                              ▼
                                                     ┌──────────────┐
                                                     │  Pattern     │
                                                     │  Discovery   │
                                                     │  Agent       │
                                                     └──────────────┘
                                                              │
                                                              ▼
                                                     ┌──────────────┐
                                                     │  HTML Report │
                                                     │  Agent       │
                                                     │  (Jinja2 +   │
                                                     │  Chart.js)   │
                                                     └──────────────┘
```

### Agent Responsibilities

| Agent | Responsibility |
|-------|---------------|
| **Supervisor** | Orchestrates the 7-phase pipeline, manages progress tracking via Rich, persists results to SQLite |
| **Research** | Merges web-researched dataset (100 apps) with category defaults. Queries Composio SDK for toolkit discovery |
| **Evidence** | Grades evidence quality per app (high/medium/low), surfaces gaps |
| **Verification** | Stratified 20-app cross-check (2 per category). Compares both first-pass and final values against independently verified expected values. Reports 78.3% → 98.3% accuracy |
| **Confidence** | Assigns HIGH/MEDIUM/LOW based on research completeness and verification corrections |
| **Human Review** | Flags only enterprise gates, low-buildability, and contradictions — not every row |
| **Pattern Discovery** | Generates auth distribution, access analysis, MCP adoption, top blockers, category insights |
| **HTML Report** | Renders Jinja2 template with TailwindCSS + Chart.js — interactive table, charts, decision board |

---

## Quick Start

### Prerequisites
- Python 3.12+
- `uv` (fast package manager, [install](https://docs.astral.sh/uv/))
- A Composio API key (optional — pipeline works without it for deterministic mode)

### One-command execution

```bash
# Clone, configure, run
cp .env.example .env
# Edit .env with your COMPOSIO_API_KEY (optional)
uv run python -m cli.main run-pipeline
```

This runs:
1. **Research** — 100 apps processed through all 7 phases
2. **HTML Report** — interactive case study generated at `frontend/report.html`

### Individual commands

```bash
### Environment Variables

You need to provide a Composio API key and a Gemini API key to use the autonomous agent:
```bash
COMPOSIO_API_KEY=your_composio_api_key
GEMINI_API_KEY=your_gemini_api_key
```

### Where are the API Keys Used?

- **`COMPOSIO_API_KEY`**: It is used in two key places:
  1. In `backend/composio_client.py` to authenticate `client.apps.list()`, letting the pipeline check which toolkits Composio already supports in production natively.
  2. In `agents/agentic.py` to initialize the `Composio` client which securely fetches MCP tools (like EXA_SEARCH) for the LLM using `composio-langchain`.
- **`GEMINI_API_KEY`**: Used in `agents/agentic.py` to power the underlying Langchain reasoning via `ChatGoogleGenerativeAI(model="gemini-1.5-flash")` which reads SaaS documentation autonomously.

### How is Composio's MCP utilized?

The pipeline uses Composio's SDK to securely fetch backend tools into Langchain's native format. Rather than writing custom web scraping code, the script asks Composio for the `EXA_SEARCH` action. Composio translates these backend tools into the standardized Model Context Protocol (MCP) schema via Langchain (`composio-langchain`), passing it to the Gemini LLM agent, executing the LLM's tool calls, and returning the results seamlessly. 

## Running the Pipeline

To run the pipeline deterministically (fast, using the verified sample dataset):
```bash
uv run python -m cli.main run-pipeline
```

To run the pipeline **agentically** using Gemini 1.5 Flash and Composio MCP to research unverified apps (this will consume LLM tokens):
```bash
uv run python -m cli.main run-pipeline --agentic --limit 10
```
# Serve locally (FastAPI or static)
uv run python -m cli.main serve --port 8000 --backend fastapi
uv run python -m cli.main serve --port 8000 --backend static

# Deploy to Vercel
uv run python -m cli.main deploy --target vercel
npx vercel deploy --prod
```

---

## Project Structure

```
├── backend/
│   ├── __init__.py
│   ├── api.py                  # FastAPI application
│   ├── composio_client.py      # Composio SDK wrapper (toolkit, MCP, managed auth)
│   ├── config.py               # Pydantic Settings from .env
│   ├── database.py             # SQLite persistence layer
│   └── models.py               # Pydantic schemas
├── agents/
│   ├── __init__.py
│   ├── supervisor.py           # 7-phase pipeline orchestrator
│   ├── evidence.py             # Evidence quality grading
│   ├── confidence.py           # Confidence scoring (HIGH/MEDIUM/LOW)
│   ├── human_review.py         # Human review queue generation
│   └── patterns.py             # Business insight discovery
├── research/
│   ├── __init__.py
│   ├── app_list.py             # 100 app definitions in 10 categories
│   ├── dataset.py              # Web-researched profiles (evidence-backed)
│   └── researcher.py           # Core research + stats computation
├── verification/
│   ├── __init__.py
│   └── verifier.py             # Independent verification pass (20-app stratified)
├── cli/
│   ├── __init__.py
│   └── main.py                 # Typer CLI (research, verify, analyze, build-report, serve, deploy, run-pipeline)
├── reports/
│   ├── __init__.py
│   └── html_report.py          # Jinja2 → HTML report generator
├── frontend/
│   ├── templates/
│   │   └── report.html.j2      # Jinja2 template (TailwindCSS + Chart.js)
│   ├── static/                 # Static assets
│   └── report.html             # Generated output
├── data/
│   ├── research.json           # Pipeline output
│   ├── verification.json       # Verification results
│   └── research.db             # SQLite checkpoint database
├── .env                        # Environment variables (not committed)
├── .env.example                # Environment variable template
├── .github/workflows/pipeline.yml  # Scheduled weekly research
├── Dockerfile                  # Containerized execution
├── docker-compose.yml          # Multi-service Docker setup
├── pyproject.toml              # Python project config + CLI entry point
└── README.md                   # This file
```

---

## Composio Integration

The platform uses the official Composio SDK for:

| Capability | Implementation |
|-----------|---------------|
| **Toolkit Discovery** | `composio_client.discover_apps()` — lists all apps via `client.apps.list()` |
| **Toolkit Check** | `composio_client.check_toolkit(app)` — SDK lookup with known-app fallback |
| **MCP Discovery** | `composio_client.check_mcp(app)` — checks `client.mcp.list()` for matching entries |
| **Connected Accounts** | `composio_client.get_connected_accounts()` — lists existing integrations |
| **Managed Auth** | Per-app auth scheme detection from SDK metadata |
| **Demand Ranking** | Internal Composio top-25 demand list |

All SDK calls are guarded: if `COMPOSIO_API_KEY` is not set, the pipeline falls back to deterministic mode with known-supported app data.

---

## Verification Strategy

```
Pass 1 (Category Defaults)
  ↓ accuracy = 78.3% (47/60 fields match expected)
  ↓
Web Research (100 apps profiled against official docs)
  ↓
Pass 2 (Verified Dataset)
  ↓ accuracy = 98.3% (59/60 fields match expected)
  ↓
20.0 percentage point improvement
  ↓
1 remaining miss: Mermaid CLI auth ("None (no auth)" vs "None (no authentication required)")
  — formatting nuance, not a data error
```

**Methodology:** 20-app stratified sample (2 per category). Each field (auth, access, api) is compared against independently verified expected values from official developer documentation using fuzzy matching that tolerates category-level vs detailed values.

---

## Output Schema

Every app in the research dataset produces:

```json
{
  "id": 1,
  "app": "Salesforce",
  "category": "CRM & Sales",
  "auth": "OAuth 2.0 (JWT Bearer, Web Server, Device, Client Credentials)",
  "access": "Free Developer Edition (15K API calls/day); production needs org",
  "api": "REST + SOAP + GraphQL + Bulk + Streaming + Pub/Sub + Metadata",
  "mcp": "No first-party MCP; community MCP servers exist",
  "verdict": "High potential: free dev edition has full API access",
  "evidence": "https://developer.salesforce.com/docs/...",
  "confidence": "HIGH",
  "composio_supported": true,
  "composio_tools": 200,
  "composio_managed_auth": true,
  "human_follow_up": false
}
```

---

## Current Results

| Metric | Value |
|--------|-------|
| Apps researched | 100 |
| Categories | 10 (10 per category) |
| High confidence | 89 |
| Medium confidence | 11 |
| Low confidence | 0 |
| Needs human review | 13 (enterprise gates + low buildability) |
| First-pass accuracy | 78.3% |
| Research accuracy | 98.3% |
| MCP signals | 39 apps |
| Composio supported | 16 apps |
| Composio total tools | ~2,410 |
| Auth: OAuth2 | 73% |
| Auth: API Key | 19% |
| Auth: Bearer Token | 5% |
| Auth: Basic Auth | 1% |
| Access: Self-serve | 55% |
| Access: Paid plan | 25% |
| Access: Enterprise gate | 12% |
| Access: Review gate | 8% |

---

## Engineering Decisions

1. **Deterministic dataset + web research** — All 100 apps have manually verified profiles against official developer docs. This produces reliable results without LLM hallucination risk.

2. **Fuzzy verification matching** — Category defaults ("OAuth2") should match detailed researched values ("OAuth 2.0 (JWT Bearer, Web Server, Device)"). The fuzzy matcher uses substring containment and family-level matching rather than exact string comparison.

3. **Conservative confidence** — "HIGH" requires researched + no verification corrections. "MEDIUM" means researched but verification flagged a discrepancy (usually first_pass vs final formatting differences). "LOW" only when unresearched or genuine contradiction.

4. **Human review is sparse** — Only 13 of 100 apps flagged: enterprise gates that need partnership outreach, and low-buildability apps that need commercial validation. Not every row goes to review.

5. **SQLite checkpoint** — The pipeline persists to SQLite for recovery and debugging. If the pipeline crashes mid-run, partial results are available.

6. **Composio SDK as source of truth** — Toolkit support and tool counts come from the SDK, not a hardcoded table. The demand rank is hardcoded (internal Composio data; not publicly queryable).

---

## Limitations

- **Live web browsing not implemented** — Current dataset is deterministic (web-researched manually). A Firecrawl/Tavily agent for live re-checking would be the next upgrade.
- **20-app verification is directional** — The 20-app stratified sample gives confidence in the dataset direction, not statistical significance per category.
- **Auth verification is doc-only** — We check documentation, not actual OAuth handshakes. A production-gate check would run real OAuth flows.
- **MCP data is static** — MCP availability changes rapidly. The dataset reflects July 2026 research.
- **No asyncio** — Pipeline is synchronous. Each phase blocks. For 100 apps this is fine (~2.4s); for 1000 apps an async refactor would help.

---

## Future Roadmap

- [ ] Live web research via Composio MCP + Firecrawl
- [ ] AI-driven verification (DeepSeek R1 or Gemini to cross-check docs)
- [ ] asyncio refactor for concurrent research
- [ ] Production OAuth handshake verification
- [ ] Weekly scheduled MCP discovery
- [ ] Category-level drill-down in HTML report
- [ ] Export to CSV/Google Sheets for partnerships team
- [ ] Slack bot for human review notifications
- [ ] Grafana dashboard for pipeline observability

---

## License
