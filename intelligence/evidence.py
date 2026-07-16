"""Evidence Agent: collects, grades, and manages evidence sources."""

from __future__ import annotations

from typing import Any

from rich.console import Console

console = Console()

EVIDENCE_GRADE_MAP: dict[str, str] = {
    "high": "Official developer documentation confirmed",
    "medium": "Source available but not directly verified against docs",
    "low": "No direct evidence source; category default applied",
}


class EvidenceAgent:
    """Grades evidence quality per app and surfaces gaps."""

    def __init__(self, research_data: dict):
        self.rows = research_data["rows"]

    def run(self) -> dict:
        """Grade evidence for all apps and return summary."""
        console.print("[dim]Grading evidence quality...[/dim]")

        grades = {"high": 0, "medium": 0, "low": 0}
        gaps = []

        for row in self.rows:
            grade = self._grade(row)
            grades[grade] += 1
            if grade == "low":
                gaps.append({
                    "app": row["app"],
                    "category": row["category"],
                    "reason": "No researched evidence; category default used",
                })
            elif grade == "medium" and not row.get("evidence"):
                gaps.append({
                    "app": row["app"],
                    "category": row["category"],
                    "reason": "Evidence URL missing despite research claims",
                })

        result = {
            "total": len(self.rows),
            "grade_counts": grades,
            "high_pct": round(grades["high"] / len(self.rows) * 100, 1),
            "evidence_gaps": gaps[:20],
            "gap_count": len(gaps),
        }

        console.print(f"  [green]✓[/green] {grades['high']} high-grade evidence")
        console.print(f"  [yellow]![/yellow] {grades['low']} apps without direct evidence")
        if gaps:
            console.print(f"  [red]![/red] {len(gaps)} evidence gaps identified")

        return result

    def _grade(self, row: dict) -> str:
        """Assign evidence grade based on available data."""
        if row.get("source_note", "").startswith("Web-researched"):
            return "high"
        if row.get("evidence"):
            return "medium"
        return "low"
