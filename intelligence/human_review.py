"""Human Review Queue: flags only rows that truly need manual inspection.

Triggers:
- LOW confidence (contradictions or missing evidence)
- MEDIUM confidence where evidence gaps exist
- Apps with enterprise gates or partnership gates requiring outreach
"""

from __future__ import annotations

from typing import Any

from rich.console import Console
from rich.table import Table
from rich import box

console = Console()


class HumanReviewAgent:
    """Generates a compact human-review queue from research data."""

    def __init__(self, research_data: dict, confidence_assignments: list[dict] | None = None):
        self.rows = research_data["rows"]
        self.by_name = {r["app"]: r for r in self.rows}
        self.assignments = confidence_assignments or []

    def run(self) -> dict:
        """Build and return the human review queue."""
        console.print("[dim]Identifying items for human review...[/dim]")

        queue = self._build_queue()
        self._print_queue(queue)

        return {
            "total_in_queue": len(queue),
            "total_apps": len(self.rows),
            "pct_needs_review": round(len(queue) / len(self.rows) * 100, 1),
            "queue": queue,
            "instructions": [
                "Review each row's 'reason' field.",
                "For 'Missing documentation' — find official dev docs and update the evidence URL.",
                "For 'Contradiction detected' — verify the correct value and update the dataset.",
                "For 'Enterprise gate / outreach' — route to partnerships team.",
                "Mark as reviewed by setting confidence=HIGH and needs_review=False.",
            ],
        }

    def _build_queue(self) -> list[dict]:
        """Determine which apps need human review."""
        assignment_map = {a["app"]: a for a in self.assignments} if self.assignments else {}
        queue = []

        for row in self.rows:
            reasons = []
            app = row["app"]

            conf = assignment_map.get(app, {})

            # Trigger 1: LOW confidence
            if conf.get("confidence") == "LOW":
                contradictions = conf.get("contradictions")
                if contradictions:
                    reasons.append(f"Contradiction detected: {'; '.join(contradictions[:2])}")
                else:
                    reasons.append("Missing researched data")

            # Trigger 2: enterprise gates -> outreach
            access = (row.get("access") or "").lower()
            if any(w in access for w in ["enterprise gate", "contact sales", "no self-serve", "enterprise only"]):
                reasons.append("Enterprise gate — route to partnerships")

            # Trigger 3: low verdict
            verdict = (row.get("verdict") or "")
            if verdict.startswith("Low"):
                reasons.append("Low buildability — verify before investing")

            # Trigger 4: evidence missing
            if not row.get("evidence") and not row.get("source_note", "").startswith("Web-researched"):
                reasons.append("No evidence URL provided")

            if reasons:
                queue.append({
                    "id": row["id"],
                    "app": app,
                    "category": row["category"],
                    "confidence": conf.get("confidence", "LOW"),
                    "reasons": reasons,
                    "access": row.get("access", ""),
                    "verdict": verdict,
                })

        return sorted(queue, key=lambda x: x["id"])

    def _print_queue(self, queue: list[dict]):
        if not queue:
            console.print("  [green]✓[/green] No apps need human review!")
            return

        table = Table(title=f"[bold]Human Review Queue ({len(queue)} items)[/bold]", box=box.ROUNDED)
        table.add_column("ID", style="dim", width=4)
        table.add_column("App", style="cyan")
        table.add_column("Confidence", width=8)
        table.add_column("Reasons", style="yellow")

        for item in queue[:25]:
            reasons_short = item["reasons"][0][:80]
            if len(item["reasons"]) > 1:
                reasons_short += f" (+{len(item['reasons'])-1} more)"
            table.add_row(
                str(item["id"]),
                item["app"],
                item["confidence"],
                reasons_short,
            )

        if len(queue) > 25:
            console.print(f"  [dim]... and {len(queue) - 25} more items[/dim]")

        console.print(table)
