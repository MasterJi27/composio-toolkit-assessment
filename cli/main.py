"""Typer CLI for the Composio Product Research Platform."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Force UTF-8 on Windows to support Rich rendering
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")

import typer
from rich.console import Console
from rich import print as rprint

from services.config import settings
from services.database import db
from intelligence.supervisor import SupervisorAgent

cli = typer.Typer(
    name="composio-research",
    help="Composio Product Research Platform — Autonomous multi-agent app research",
    add_completion=False,
)
console = Console()


@cli.command("research")
def research(
    live_check: bool = typer.Option(False, "--live-check", help="Probe evidence URLs for reachability"),
    agentic: bool = typer.Option(False, "--agentic", help="Use LLM and Composio MCP to research unverified apps"),
    limit: int = typer.Option(100, "--limit", help="Maximum apps to research"),
    output: Path = typer.Option(
        settings.research_json, "--output", "-o", help="Output JSON path"
    ),
):
    """Run the full multi-agent research pipeline on all 100 apps."""
    rprint("[bold cyan]Composio Product Research Platform[/bold cyan]")
    rprint("[dim]Researching apps with autonomous agents...[/dim]\n")

    supervisor = SupervisorAgent()
    result = supervisor.run_pipeline(live_check=live_check, agentic=agentic, limit=limit)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")

    rprint(f"\n[green]✓[/green] Results written to {output}")
    rprint(f"[green]✓[/green] {result['total_apps']} apps processed")
    rprint(f"[green]✓[/green] {result.get('high_confidence', 0)} high confidence")
    rq = result.get("review_queue", {})
    rprint(f"[green]✓[/green] {rq.get('total_in_queue', 0)} need human review")


@cli.command()
def verify():
    """Run only the verification pass on existing research data."""
    from evaluation.verifier import VerificationAgent

    if not settings.research_json.exists():
        rprint("[red]✗[/red] No research data found. Run 'composio-research research' first.")
        raise typer.Exit(1)

    data = json.loads(settings.research_json.read_text(encoding="utf-8"))
    verifier = VerificationAgent(data)
    result = verifier.run()

    settings.verification_json.parent.mkdir(parents=True, exist_ok=True)
    settings.verification_json.write_text(json.dumps(result, indent=2), encoding="utf-8")
    rprint(f"[green]✓[/green] Verification written to {settings.verification_json}")

    v = result["after_research_loop"]
    rprint(f"[green]✓[/green] Final accuracy: {v['accuracy']*100:.1f}% ({v['hits']}/{v['fields']})")


@cli.command()
def analyze():
    """Run pattern discovery on existing research data."""
    from intelligence.patterns import PatternDiscoveryAgent

    if not settings.research_json.exists():
        rprint("[red]✗[/red] No research data found. Run 'composio-research research' first.")
        raise typer.Exit(1)

    data = json.loads(settings.research_json.read_text(encoding="utf-8"))
    agent = PatternDiscoveryAgent(data)
    agent.discover()


@cli.command()
def build_report(
    output: Path = typer.Option(
        settings.report_dir / "report.html", "--output", "-o", help="Output HTML path"
    ),
):
    """Generate the interactive HTML case study report."""
    from reports.html_report import generate_report

    if not settings.research_json.exists():
        rprint("[red]✗[/red] No research data found. Run 'composio-research research' first.")
        raise typer.Exit(1)

    data = json.loads(settings.research_json.read_text(encoding="utf-8"))

    if settings.verification_json.exists():
        verification = json.loads(settings.verification_json.read_text(encoding="utf-8"))
        data["evaluation"] = verification
    else:
        data["evaluation"] = {}

    generate_report(data, output)
    rprint(f"[green]✓[/green] Report generated at {output}")


@cli.command()
def serve(
    port: int = typer.Option(8000, "--port", "-p", help="Port to serve on"),
    backend: str = typer.Option("fastapi", "--backend", "-b", help="Server backend (fastapi or static)"),
):
    """Serve the generated report via HTTP."""
    if backend == "fastapi":
        import uvicorn
        rprint(f"[green]→[/green] FastAPI server at http://localhost:{port}")
        rprint("[dim]Press Ctrl+C to stop[/dim]")
        from services.api import app
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
    else:
        import http.server
        import socketserver
        os.chdir(str(settings.report_dir))
        handler = http.server.SimpleHTTPRequestHandler
        rprint(f"[green]→[/green] Serving {settings.report_dir}/ at http://localhost:{port}")
        rprint("[dim]Press Ctrl+C to stop[/dim]")
        with socketserver.TCPServer(("", port), handler) as httpd:
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                rprint("\n[yellow]Server stopped.[/yellow]")


import os
import subprocess
import sys


@cli.command()
def run_pipeline(
    skip_report: bool = typer.Option(False, "--skip-report", help="Skip HTML report generation"),
    live_check: bool = typer.Option(False, "--live-check", help="Probe evidence URLs for reachability"),
    agentic: bool = typer.Option(False, "--agentic", help="Use LLM and Composio MCP to research unverified apps"),
    limit: int = typer.Option(100, "--limit", help="Maximum apps to research"),
):
    """Run the full pipeline end-to-end: research → verify → build-report."""
    rprint("[bold cyan]Composio Product Research Platform — Full Pipeline[/bold cyan]")
    rprint("[dim]Running research, verification, analysis, and report generation...[/dim]\n")

    exit_code = 0

    def _run(cmd: list[str], label: str):
        nonlocal exit_code
        rprint(f"\n[bold]━━─ {label} ─━━[/bold]")
        result = subprocess.run(cmd, capture_output=False)
        if result.returncode != 0:
            rprint(f"[red]✗ {label} failed with code {result.returncode}[/red]")
            exit_code = result.returncode
            raise typer.Exit(result.returncode)

    research_cmd = [sys.executable, "-m", "cli.main", "research"]
    if live_check:
        research_cmd.append("--live-check")
    if agentic:
        research_cmd.append("--agentic")
    research_cmd.extend(["--limit", str(limit)])
        
    _run(research_cmd, "Research")
    if not skip_report:
        _run([sys.executable, "-m", "cli.main", "build-report"], "HTML Report")

    if exit_code == 0:
        rprint(f"\n[bold green]✓ Pipeline complete[/bold green]")
        report_path = settings.report_dir / "report.html"
        if report_path.exists():
            rprint(f"[green]  Report: file://{report_path}[/green]")


@cli.command()
def deploy(
    target: str = typer.Option("vercel", "--target", "-t", help="Deployment target (vercel)"),
):
    """Deploy the report to production."""
    rprint(f"[bold cyan]Deploying to {target}...[/bold cyan]")

    if not (settings.report_dir / "report.html").exists():
        rprint("[yellow]! Report not found. Building first...[/yellow]")
        subprocess.run([sys.executable, "-m", "cli.main", "build-report"])

    if target == "vercel":
        vercel_json = Path("vercel.json")
        if not vercel_json.exists():
            import json as _json
            vercel_json.write_text(_json.dumps({
                "version": 2,
                "builds": [{"src": "frontend/**", "use": "@vercel/static"}],
                "routes": [{"src": "/(.*)", "dest": "/frontend/$1"}],
            }, indent=2), encoding="utf-8")
            rprint("[green]✓ vercel.json created[/green]")
        rprint("[yellow]→ Run 'npx vercel deploy --prod' to deploy[/yellow]")
    else:
        rprint(f"[red]✗ Unknown target: {target}[/red]")
        raise typer.Exit(1)


@cli.callback()
def main_callback():
    """Composio Product Research Platform."""
    pass


def entry_point():
    cli()


if __name__ == "__main__":
    entry_point()
