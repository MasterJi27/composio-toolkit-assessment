"""FastAPI application for production report serving and pipeline API."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from backend.config import settings

app = FastAPI(
    title="Composio Product Research API",
    description="Serve research reports and pipeline results via API",
    version="1.0.0",
)

if (settings.report_dir / "static").exists():
    app.mount("/static", StaticFiles(directory=str(settings.report_dir / "static")), name="static")

if (settings.report_dir / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(settings.report_dir / "assets")), name="assets")


@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the main research report."""
    report_path = settings.report_dir / "report.html"
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="Report not found. Run 'composio-research build-report' first.")
    return HTMLResponse(report_path.read_text(encoding="utf-8"))


@app.get("/api/research.json")
async def research_json():
    """Return the raw research data as JSON."""
    if not settings.research_json.exists():
        raise HTTPException(status_code=404, detail="Research data not found. Run 'composio-research research' first.")
    return json.loads(settings.research_json.read_text(encoding="utf-8"))


@app.get("/api/verification.json")
async def verification_json():
    """Return verification results."""
    path = settings.verification_json
    if not path.exists():
        raise HTTPException(status_code=404, detail="Verification data not found.")
    return json.loads(path.read_text(encoding="utf-8"))


@app.get("/api/stats")
async def stats():
    """Return summary statistics."""
    if not settings.research_json.exists():
        raise HTTPException(status_code=404)
    data = json.loads(settings.research_json.read_text(encoding="utf-8"))
    return data.get("stats", {})


@app.get("/api/review-queue")
async def review_queue():
    """Return the human review queue."""
    if not settings.research_json.exists():
        raise HTTPException(status_code=404)
    data = json.loads(settings.research_json.read_text(encoding="utf-8"))
    return data.get("review_queue", {})


@app.get("/favicon.ico")
async def favicon():
    return FileResponse(settings.report_dir / "static" / "favicon.ico") if (settings.report_dir / "static" / "favicon.ico").exists() else HTMLResponse("")
