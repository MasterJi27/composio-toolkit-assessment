# Composio toolkit readiness case study

This repository is the take-home submission package for the AI Product Ops Intern assessment. The deliverable is the self-contained case study at [`site/index.html`](site/index.html), generated from a 100-app research dataset.

## Run locally

```powershell
python research_agent.py
python verify.py
python generate_site.py
python -m http.server 8000
```

Open `http://localhost:8000/site/`.

### Run with Gemini 3.1 Flash-Lite AI Agent:

```powershell
# Set your Gemini API Key in .env
# GEMINI_API_KEY=AIzaSy...
python research_agent.py --use-ai --live-check
python verify.py
python generate_site.py
```

### Run with Kimchi CLI (CAST AI kimi-k2.7):

```powershell
# Set your Kimchi API Key in .env
# KIMCHI_API_KEY=castai_v1_...
# KIMCHI_MODEL=kimi-k2.7
python research_agent.py --use-kimchi --live-check
python verify.py
python generate_site.py
```

The live probe only reports reachability. It never treats a timeout or HTTP error as proof that an API is absent. If the API keys are rate-limited or unavailable, the agent automatically falls back to the deterministic offline dataset to guarantee 100% execution success.

## What the pipeline does

1. `research_agent.py` normalizes the 100 apps from the assignment, preserves the supplied documentation hints, applies category baselines, and adds targeted profiles for high-demand or high-risk apps. The output is `data/research.json`.
2. `verify.py` performs a small stratified sample across categories and access risk. It compares first-pass decisions with reviewed decisions and writes `data/verification.json`.
3. `generate_site.py` turns both artifacts into one interactive HTML page with the headline, findings, process, evidence matrix, proof trigger, and verification limits.

The agent is intentionally dependency-free and secret-free. A future Composio/MCP provider can replace the source adapter without changing the schema or verification loop. The current artifact does not claim that an API landing page proves credential availability; rows with unresolved commercial or product ambiguity are explicitly queued for human follow-up.

## Evidence boundary

The 100-row matrix is a sourcing map, not a claim that every app has been contract-level audited. Forty-one rows have targeted app-specific profiles; the rest inherit a conservative category baseline and are visibly marked for follow-up. The 12-row verification sample is backed by official source pages and reports field-level accuracy only on that sample.

## Key result

The strongest pattern is: **the API surface is usually available; access is the bottleneck**. Developer infrastructure and productivity apps form the cleanest self-serve queue. Fintech, advertising/social permissions, enterprise media, and product-specific MCP surfaces need review, compliance, or partnership work.

## Submission checklist

- Deploy the `site/` directory as a static site.
- Push this repository and submit its URL.
- Submit the deployed `site/index.html` URL.
- Before final submission, rerun `research_agent.py --live-check`, review the evidence links, and re-run `verify.py` because API policies and plan gates change.

The repository is prepared locally; no external repository, deployment, or application form was created or submitted from this workspace.
