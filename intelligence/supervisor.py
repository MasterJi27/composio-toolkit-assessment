"""Supervisor Agent: orchestrates the multi-agent research pipeline.

Responsible for:
- Queue management and scheduling
- Progress tracking with Rich
- Checkpoint recovery via SQLite
- Escalation to human review
"""

from __future__ import annotations

import json
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskID
from rich.panel import Panel
from rich.table import Table
from rich import box

from services.config import settings
from services.database import db, AppRecord
from research.researcher import research_all, compute_stats
from evaluation.verifier import VerificationAgent
from intelligence.evidence import EvidenceAgent
from intelligence.confidence import ConfidenceAgent
from intelligence.human_review import HumanReviewAgent
from intelligence.patterns import PatternDiscoveryAgent

console = Console()


class PipelineRegistry:
    """Dynamic Registry for executing pipeline nodes with dependency resolution."""
    def __init__(self, data: dict):
        self.data = data
        self.results = {}

    def run_node(self, name: str, agent_class: Any, method: str = "run", deps: list[Any] = None):
        console.rule(f"[bold green]Phase: {name.replace('_', ' ').title()}[/bold green]")
        # Instantiate with data and dependencies
        agent_args = [self.data]
        if deps:
            agent_args.extend(deps)
        
        agent_instance = agent_class(*agent_args)
        run_func = getattr(agent_instance, method)
        self.results[name] = run_func()
        return self.results[name]


class SupervisorAgent:
    """Master orchestrator for the multi-agent research pipeline."""

    def __init__(self):
        self.research_data: Optional[dict] = None
        self.evidence_results: Optional[dict] = None
        self.verification_results: Optional[dict] = None
        self.confidence_assignments: Optional[list[dict]] = None
        self.review_queue: Optional[dict] = None
        self.insights: Optional[dict] = None
        self._update_status("idle", "Idle")

    def _update_status(self, status: str, phase: str, progress: int = 0, total: int = 100, error_message: str = ""):
        status_file = settings.data_dir / "pipeline_status.json"
        status_data = {
            "status": status,
            "phase": phase,
            "progress": progress,
            "total": total,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "error_message": error_message
        }
        try:
            status_file.write_text(json.dumps(status_data, indent=2), encoding="utf-8")
        except Exception:
            pass

    def _apply_confidence(self):
        """Backfill confidence scores into research_data rows and recalc stats."""
        if not self.confidence_assignments:
            return
        by_name = {a["app"]: a for a in self.confidence_assignments}
        for row in self.research_data["rows"]:
            conf = by_name.get(row["app"], {})
            row["confidence"] = conf.get("confidence", "LOW")
            row["human_follow_up"] = conf.get("needs_review", True)
        # Recalculate stats after confidence assignment
        from collections import Counter
        counts = Counter(r["confidence"] for r in self.research_data["rows"])
        needs = sum(1 for r in self.research_data["rows"] if r.get("human_follow_up", True))
        self.research_data["stats"]["high_confidence"] = counts.get("HIGH", 0)
        self.research_data["stats"]["medium_confidence"] = counts.get("MEDIUM", 0)
        self.research_data["stats"]["low_confidence"] = counts.get("LOW", 0)
        self.research_data["stats"]["needs_review"] = needs

    def run_pipeline(self, live_check: bool = False, agentic: bool = False, limit: int = 100) -> dict:
        """Run all phases registry-driven."""
        try:
            start_time = time.time()
            self._update_status("running", "Research", progress=0, total=limit)

            # Phase 1: Research
            from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn, MofNCompleteColumn

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                MofNCompleteColumn(),
                TextColumn("•"),
                TimeRemainingColumn(),
                console=console,
            ) as progress:
                task = progress.add_task(f"[yellow]Researching {limit} apps...", total=limit)
                
                def on_progress():
                    progress.update(task, advance=1)
                    p_task = progress.tasks[task]
                    self._update_status("running", "Research", progress=int(p_task.completed), total=limit)
                    
                self.research_data = research_all(live_check=live_check, agentic=agentic, limit=limit, progress_callback=on_progress)
                
                progress.update(task, description="[green]Research complete!")

            stats = self.research_data["stats"]
            console.print(f"  [green]✓[/green] {stats['total']} apps researched")
            console.print(f"  [green]✓[/green] {stats['researched']} with web-researched profiles")
            console.print(f"  [green]✓[/green] {stats['high_confidence']} high confidence")
            console.print(f"  [yellow]![/yellow] {stats['needs_review']} need review")

            # Initialize Pipeline Registry
            registry = PipelineRegistry(self.research_data)

            # Phase 2: Evidence Grading
            self._update_status("running", "Evidence", progress=limit, total=limit)
            self.evidence_results = registry.run_node("evidence", EvidenceAgent)

            # Phase 3: Verification
            self._update_status("running", "Verification", progress=limit, total=limit)
            self.verification_results = registry.run_node("verification", VerificationAgent)

            # Phase 4: Confidence Assignment
            self._update_status("running", "Confidence", progress=limit, total=limit)
            confidence_result = registry.run_node("confidence", ConfidenceAgent, deps=[self.verification_results])
            self.confidence_assignments = confidence_result["assignments"]
            self._apply_confidence()

            # Phase 5: Human Review Queue
            self._update_status("running", "Human Review", progress=limit, total=limit)
            self.review_queue = registry.run_node("human_review", HumanReviewAgent, deps=[self.confidence_assignments])

            # Phase 6: Pattern Discovery
            self._update_status("running", "Patterns", progress=limit, total=limit)
            self.insights = registry.run_node("patterns", PatternDiscoveryAgent, method="discover")

            # Phase 7: Persist
            console.rule("[bold green]Phase: Persisting Results[/bold green]")
            self._update_status("running", "Report", progress=limit, total=limit)
            self._persist()

            elapsed = time.time() - start_time
            self._update_status("completed", "Idle", progress=limit, total=limit)
            console.rule("[bold green]Pipeline Complete[/bold green]")
            console.print(Panel.fit(
                f"[bold white]Summary[/bold white]\n"
                f"  Apps researched: {stats['total']}\n"
                f"  High confidence: {stats['high_confidence']}\n"
                f"  Medium confidence: {stats['medium_confidence']}\n"
                f"  Low confidence: {stats['low_confidence']}\n"
                f"  Needs human review: {self.review_queue['total_in_queue'] if self.review_queue else 0}\n"
                f"  MCP signals: {stats['mcp_count']}\n"
                f"  Composio already supports: {stats['composio_supported']}\n"
                f"  Evidence gaps: {self.evidence_results['gap_count'] if self.evidence_results else 0}\n"
                f"  Time elapsed: {elapsed:.1f}s",
                border_style="green",
            ))

            return self._build_output()
        except Exception as e:
            self._update_status("error", "Idle", error_message=str(e))
            raise

    def _persist(self):
        """Persist all records to SQLite."""
        for row in self.research_data["rows"]:
            record = AppRecord(
                id=row["id"],
                app=row["app"],
                category=row["category"],
                auth=row["auth"],
                access=row["access"],
                api=row["api"],
                mcp=row.get("mcp", ""),
                verdict=row["verdict"],
                evidence=row.get("evidence", ""),
                evidence_grade=row.get("evidence_grade", ""),
                confidence=row.get("confidence", "LOW"),
                needs_review=row.get("human_follow_up", True),
                composio_supported=row.get("composio_supported", False),
                composio_tools=row.get("composio_tools", 0),
                composio_managed_auth=row.get("composio_managed_auth", False),
                composio_demand_rank=row.get("composio_demand_rank"),
                first_pass_auth=row.get("first_pass", {}).get("auth", ""),
                first_pass_access=row.get("first_pass", {}).get("access", ""),
                first_pass_api=row.get("first_pass", {}).get("api", ""),
                first_pass_verdict=row.get("first_pass", {}).get("verdict", ""),
                source_note=row.get("source_note", ""),
                created_at=datetime.now(timezone.utc).isoformat(),
            )
            db.upsert(record)

        # Save verification
        if self.verification_results:
            (settings.data_dir / "verification.json").write_text(
                json.dumps(self.verification_results, indent=2), encoding="utf-8"
            )

    def _build_output(self) -> dict:
        """Build the final output dictionary."""
        rows_out = []
        for row in self.research_data["rows"]:
            rows_out.append({
                "id": row["id"],
                "app": row["app"],
                "category": row["category"],
                "description": row.get("description", ""),
                "auth": row["auth"],
                "access": row["access"],
                "api": row["api"],
                "mcp": row.get("mcp", ""),
                "verdict": row["verdict"],
                "evidence": row.get("evidence", ""),
                "confidence": row.get("confidence", "LOW"),
                "composio_supported": row.get("composio_supported", False),
                "composio_tools": row.get("composio_tools", 0),
                "composio_managed_auth": row.get("composio_managed_auth", False),
                "composio_demand_rank": row.get("composio_demand_rank"),
                "source_note": row.get("source_note", ""),
                "evidence_grade": row.get("evidence_grade", ""),
                "first_pass": row.get("first_pass", {}),
                "final": row.get("final", {}),
                "human_follow_up": row.get("human_follow_up", True),
            })

        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "method": "Multi-Agent Pipeline: Supervisor → Research → Evidence → Verification → Confidence → HumanReview → Patterns",
            "total_apps": len(rows_out),
            "researched": self.research_data["stats"]["researched"],
            "high_confidence": self.research_data["stats"]["high_confidence"],
            "medium_confidence": self.research_data["stats"]["medium_confidence"],
            "low_confidence": self.research_data["stats"]["low_confidence"],
            "needs_review": self.research_data["stats"]["needs_review"],
            "rows": rows_out,
            "stats": self.research_data["stats"],
            "insights": self.insights or {},
            "evaluation": self.verification_results or {},
            "evidence": self.evidence_results or {},
            "review_queue": self.review_queue or {},
        }
