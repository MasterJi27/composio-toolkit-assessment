"""HTML Report Agent: generates the interactive case study HTML page.

Uses Jinja2 template at frontend/templates/report.html.j2.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from backend.config import settings


def generate_report(data: dict, output_path: Path):
    """Generate the interactive HTML report from research data using Jinja2."""
    template_dir = settings.report_dir / "templates"
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(["html", "xml"]),
    )

    # Build serializable versions of the data
    rows = data.get("rows", [])
    stats = data.get("stats", {})
    insights = data.get("insights", {})
    verification = data.get("verification", {})

    # Serialize to JSON for embedding
    rows_json = json.dumps(rows, ensure_ascii=False).replace("</", "<\\/")
    stats_json = json.dumps(stats, ensure_ascii=False).replace("</", "<\\/")
    insights_json = json.dumps(insights, ensure_ascii=False).replace("</", "<\\/")
    ver_json = json.dumps(verification, ensure_ascii=False).replace("</", "<\\/")

    frontend_dir = settings.report_dir
    tailwind_js = (frontend_dir / "assets" / "tailwind.js").read_text(encoding="utf-8") if (frontend_dir / "assets" / "tailwind.js").exists() else ""
    chart_js = (frontend_dir / "assets" / "chart.js").read_text(encoding="utf-8") if (frontend_dir / "assets" / "chart.js").exists() else ""
    mermaid_js = (frontend_dir / "assets" / "mermaid.js").read_text(encoding="utf-8") if (frontend_dir / "assets" / "mermaid.js").exists() else ""

    template = env.get_template("report.html.j2")
    html = template.render(
        rows_json=rows_json,
        stats_json=stats_json,
        insights_json=insights_json,
        ver_json=ver_json,
        tailwind_js=tailwind_js,
        chart_js=chart_js,
        mermaid_js=mermaid_js,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
