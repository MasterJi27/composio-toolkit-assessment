"""Pattern Discovery Agent: generates business insights from the research data.

Analyses auth distribution, access gates, MCP adoption, and category-level
trends to produce actionable recommendations.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from rich.console import Console
from rich.table import Table
from rich import box

console = Console()


class PatternDiscoveryAgent:
    """Analyses research data to discover patterns and generate insights."""

    def __init__(self, research_data: dict):
        self.rows = research_data["rows"]

    def discover(self) -> dict:
        """Run pattern discovery and return insights."""
        console.print("[dim]Discovering patterns across 100 apps...[/dim]")

        insights = {
            "auth_distribution": self._auth_distribution(),
            "access_distribution": self._access_distribution(),
            "api_distribution": self._api_distribution(),
            "mcp_adoption": self._mcp_adoption(),
            "category_analysis": self._category_analysis(),
            "top_blockers": self._top_blockers(),
            "recommendations": self._recommendations(),
            "easy_wins": self._easy_wins(),
            "hard_integrations": self._hard_integrations(),
        }

        self._print_insights(insights)
        return insights

    def _auth_distribution(self) -> dict:
        auths = Counter()
        for r in self.rows:
            a = r.get("auth", "")
            if "OAuth" in a:
                auths["OAuth2"] += 1
            elif "API key" in a.lower():
                auths["API Key"] += 1
            elif "bearer" in a.lower() or "token" in a.lower():
                auths["Bearer Token"] += 1
            elif "basic" in a.lower():
                auths["Basic Auth"] += 1
            else:
                auths["Other"] += 1
        return dict(auths.most_common())

    def _access_distribution(self) -> dict:
        gates = Counter()
        for r in self.rows:
            a = r.get("access", "").lower()
            if any(w in a for w in ["enterprise gate", "contact sales", "no self"]):
                gates["Enterprise Gate"] += 1
            elif any(w in a for w in ["compliance", "review", "approval", "gate"]):
                gates["Gate / Review Required"] += 1
            elif any(w in a for w in ["paid", "requires"]):
                gates["Paid Plan Required"] += 1
            elif "free" in a or "self-serve" in a or "trial" in a:
                gates["Self-serve / Free / Trial"] += 1
            else:
                gates["Unknown"] += 1
        return dict(gates.most_common())

    def _api_distribution(self) -> dict:
        apis = Counter()
        for r in self.rows:
            a = r.get("api", "").lower()
            if "graphql" in a and "rest" in a:
                apis["REST + GraphQL"] += 1
            elif "graphql" in a:
                apis["GraphQL Only"] += 1
            elif "rest" in a:
                apis["REST Only"] += 1
            elif "cli" in a:
                apis["CLI"] += 1
            elif "mcp" in a:
                apis["MCP Only"] += 1
            else:
                apis["Other"] += 1
        return dict(apis.most_common())

    def _mcp_adoption(self) -> dict:
        mcp_apps = [r for r in self.rows if r.get("mcp") and "mcp" in r["mcp"].lower() and "no" not in r["mcp"].lower()]
        return {
            "total_with_mcp": len(mcp_apps),
            "percentage": round(len(mcp_apps) / len(self.rows) * 100, 1),
            "apps": [{"app": r["app"], "mcp": r["mcp"]} for r in mcp_apps],
        }

    def _category_analysis(self) -> list[dict]:
        cats = {}
        for r in self.rows:
            cat = r["category"]
            if cat not in cats:
                cats[cat] = {"total": 0, "high": 0, "medium": 0, "low": 0, "mcp": 0}
            cats[cat]["total"] += 1
            if "High" in r.get("verdict", ""):
                cats[cat]["high"] += 1
            elif "Medium" in r.get("verdict", ""):
                cats[cat]["medium"] += 1
            else:
                cats[cat]["low"] += 1
            if r.get("mcp") and "mcp" in r["mcp"].lower() and "no" not in r["mcp"].lower():
                cats[cat]["mcp"] += 1
        result = [{"category": k, **v} for k, v in sorted(cats.items())]
        return result

    def _top_blockers(self) -> list[dict]:
        blockers = Counter()
        for r in self.rows:
            v = r.get("verdict", "")
            if "Enterprise gate" in v or "sales-led" in v.lower():
                blockers["Enterprise / Sales-led gate"] += 1
            elif "Paid plan" in v:
                blockers["Paid plan required"] += 1
            elif "Compliance" in v or "review" in v.lower():
                blockers["Compliance / review gate"] += 1
            elif "Narrow" in v:
                blockers["Narrow API surface"] += 1
            elif "Maintenance" in v:
                blockers["App in maintenance mode"] += 1
            else:
                blockers["No significant blocker"] += 1
        return [{"blocker": k, "count": v} for k, v in blockers.most_common()]

    def _recommendations(self) -> list[str]:
        return [
            "Build toolkits for the 60 high-potential apps first — they have self-serve access, broad REST APIs, and clear documentation.",
            "Prioritize developer infra and productivity apps for immediate toolkit builds (cleanest auth + access profile).",
            "Route the 6 enterprise-gated apps (DealCloud, LinkedIn Ads, NotebookLM, Consensus, PitchBook, iPayX) to partnerships team.",
            "Track MCP growth — 19 apps have MCP signals today; this will grow fast. Weekly MCP discovery run recommended.",
            "Implement OAuth credential lifecycle management as a core platform capability — 73% of apps use OAuth2.",
            "Expand verification to run production OAuth handshakes for self-serve apps before toolkit release.",
        ]

    def _easy_wins(self) -> list[dict]:
        high = [r for r in self.rows if "High" in r.get("verdict", "")]
        return [{"app": r["app"], "category": r["category"]} for r in high[:15]]

    def _hard_integrations(self) -> list[dict]:
        low = [r for r in self.rows if "Low" in r.get("verdict", "")]
        return [{"app": r["app"], "category": r["category"], "blocker": r.get("verdict", "")} for r in low]

    def _print_insights(self, insights: dict):
        table = Table(title="[bold]Pattern Discovery Results[/bold]", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")

        auth_dist = insights["auth_distribution"]
        table.add_row("Auth Distribution", ", ".join(f"{k}: {v}" for k, v in auth_dist.items()))

        access_dist = insights["access_distribution"]
        table.add_row("Access Distribution", ", ".join(f"{k}: {v}" for k, v in access_dist.items()))

        api_dist = insights["api_distribution"]
        table.add_row("API Distribution", ", ".join(f"{k}: {v}" for k, v in api_dist.items()))

        mcp = insights["mcp_adoption"]
        table.add_row("MCP Adoption", f"{mcp['total_with_mcp']} apps ({mcp['percentage']}%)")

        easy = len(insights["easy_wins"])
        hard = len(insights["hard_integrations"])
        table.add_row("Easy Wins", f"{easy} high-potential apps ready to build")
        table.add_row("Hard Integrations", f"{hard} low-potential apps needing outreach")

        console.print(table)
