"""Confidence Agent: assigns confidence levels based on evidence and verification."""

from __future__ import annotations

from typing import Any

from rich.console import Console

console = Console()


class ConfidenceAgent:
    """Assigns HIGH/MEDIUM/LOW confidence per app based on evidence + verification."""

    def __init__(self, research_data: dict, verification_results: dict | None = None):
        self.rows = research_data["rows"]
        self.verification = verification_results or {}
        self.by_name = {r["app"]: r for r in self.rows}

    def run(self) -> list[dict]:
        """Score and tag each row with confidence and human_follow_up."""
        console.print("[dim]Assigning confidence levels...[/dim]")

        contradictions = self._find_contradictions()
        verified = self._verified_apps()

        assignments = []
        for row in self.rows:
            app = row["app"]
            score = self._score(row, contradictions.get(app), app in verified)
            assignments.append(score)

        summary = {
            "high": sum(1 for a in assignments if a["confidence"] == "HIGH"),
            "medium": sum(1 for a in assignments if a["confidence"] == "MEDIUM"),
            "low": sum(1 for a in assignments if a["confidence"] == "LOW"),
            "needs_review": sum(1 for a in assignments if a["needs_review"]),
            "contradictions": len(contradictions) if contradictions else 0,
        }

        console.print(f"  [green]✓[/green] {summary['high']} HIGH confidence")
        console.print(f"  [yellow]![/yellow] {summary['medium']} MEDIUM confidence")
        console.print(f"  [red]![/red] {summary['low']} LOW confidence")
        if summary["contradictions"]:
            console.print(f"  [red]![/red] {summary['contradictions']} contradictions detected")

        return {"assignments": assignments, "summary": summary}

    def _find_contradictions(self) -> dict[str, list[str]]:
        """Detect contradictions identified by the verification pass."""
        result = {}
        records = self.verification.get("records", [])
        for rec in records:
            corrections = rec.get("corrected_fields", [])
            if corrections:
                result[rec["app"]] = [
                    f"Verification corrected: {f}" for f in corrections
                ]
        return result

    def _verified_apps(self) -> set[str]:
        """Return set of apps that passed verification without corrections."""
        records = self.verification.get("records", [])
        return {r["app"] for r in records if not r.get("corrected_fields")}

    def _score(self, row: dict, contradictions: list[str] | None, verified: bool) -> dict:
        """Score a single app's confidence."""
        is_researched = row["app"] in {
            r["app"] for r in self.rows if r.get("source_note", "").startswith("Web-researched")
        }

        if is_researched and verified and not contradictions:
            confidence = "HIGH"
            needs_review = False
        elif is_researched and not contradictions:
            confidence = "HIGH"
            needs_review = False
        elif is_researched and contradictions:
            confidence = "MEDIUM"
            needs_review = False
        elif not is_researched:
            confidence = "LOW"
            needs_review = True
        else:
            confidence = "MEDIUM"
            needs_review = True

        return {
            "app": row["app"],
            "confidence": confidence,
            "needs_review": needs_review,
            "evidence_grade": "high" if is_researched else "low",
            "contradictions": contradictions,
            "verified": verified,
        }
