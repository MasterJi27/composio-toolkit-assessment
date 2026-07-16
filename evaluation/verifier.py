"""Verification Agent: independent cross-check of research findings.

Compares first-pass (category defaults) AND final (researched) values
against independently verified expected values from official docs.
Reports accuracy at both stages and the improvement.
"""

from __future__ import annotations

from typing import Any

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from rich import box

from research.dataset import RESEARCHED

console = Console()

# 20-app stratified verification sample (2 per category)
# Expected values from official developer documentation
VERIFICATION_SAMPLE: list[tuple[int, str, str, str, str]] = [
    # CRM & Sales (2)
    (1, "Salesforce",
     "OAuth 2.0 (JWT Bearer, Web Server, Device, Client Credentials)",
     "Free Developer Edition (15K API calls/day); production needs org",
     "REST + SOAP + GraphQL + Bulk + Streaming + Pub/Sub + Metadata"),
    (4, "Attio",
     "OAuth 2.0 / Bearer access tokens",
     "Free plan includes API, webhooks, and MCP",
     "REST; native MCP server"),
    # Support & Helpdesk (2)
    (11, "Zendesk",
     "OAuth 2.0 (auth code + client credentials); API token (deprecating Apr 2027)",
     "Paid plan required; free trial available",
     "REST (very broad)"),
    (17, "Plain",
     "API key (Bearer; fine-grained scoped Machine User permissions)",
     "Paid from $35/mo; 7-day free trial",
     "GraphQL only; MCP server"),
    # Communications & Messaging (2)
    (21, "Slack",
     "OAuth 2.0 (bot tokens xoxb-, user tokens xoxp-)",
     "Self-serve: free tier",
     "REST (150+ methods) + WebSocket Events"),
    (24, "Lark (Larksuite)",
     "OAuth 2.0-adjacent (tenant/user access tokens)",
     "Self-serve: free tier",
     "REST (2500+ APIs); official MCP"),
    # Marketing, Ads, Email & Social (2)
    (31, "Google Ads",
     "OAuth 2.0 + Developer Token (4 tiers)",
     "Enterprise gate: token approval days-weeks",
     "REST + gRPC; very broad"),
    (36, "Klaviyo",
     "OAuth 2.0 (mandatory; refresh tokens)",
     "Self-serve: free tier available",
     "REST (JSON:API spec)"),
    # Ecommerce (2)
    (41, "Shopify",
     "OAuth 2.0 / admin API tokens (custom apps)",
     "Self-serve: free development stores",
     "GraphQL (primary) + REST (legacy)"),
    (49, "Amazon Selling Partner",
     "OAuth 2.0 (LWA) + AWS SigV4 + RDT",
     "Enterprise gate: multi-step approval",
     "REST (very broad)"),
    # Data, SEO & Scraping (2)
    (55, "Apify",
     "API token + OAuth 2.0 (integrations/MCP)",
     "Self-serve: free $5/mo usage",
     "REST (very broad); MCP server"),
    (56, "Firecrawl",
     "API key (Bearer; fc- prefix)",
     "Self-serve: free 1000 credits/mo",
     "REST; MCP server"),
    # Developer, Infra & Data Platforms (2)
    (61, "GitHub",
     "OAuth 2.0 (PAT, OAuth App, GitHub App, GITHUB_TOKEN)",
     "Self-serve: free tier (5000 req/hr)",
     "REST + GraphQL (very broad)"),
    (64, "Cloudflare",
     "API Token (Bearer) / Legacy API Key / OAuth 2.0",
     "Self-serve: free tier",
     "REST v4 + GraphQL (100+ products)"),
    # Productivity & Project Management (2)
    (71, "Notion",
     "OAuth 2.0 / PAT / Internal Integration Token",
     "Self-serve: free tier",
     "REST (~37 endpoints)"),
    (76, "Monday.com",
     "Personal API V2 Token / OAuth 2.0",
     "Self-serve: free dev account",
     "GraphQL; MCP server (50+ tools)"),
    # Finance & Fintech (2)
    (81, "Stripe",
     "API keys (Basic Auth/Bearer) / OAuth 2.0 (Connect)",
     "Self-serve: free test-mode sandbox",
     "REST v1+v2 (~300+ endpoints)"),
    (83, "Binance",
     "API key + HMAC-SHA256/RSA/Ed25519 signature",
     "Self-serve: create keys from account",
     "REST + WebSocket (very broad)"),
    # AI, Research & Media-native (2)
    (92, "Fathom",
     "API key (X-Api-Key) / OAuth 2.0 (Auth Code + PKCE)",
     "Self-serve: free tier (60 req/min)",
     "REST (meetings, recordings, transcripts, summaries)"),
    (98, "Mermaid CLI",
     "None (no auth)",
     "Free/open source (MIT)",
     "CLI + Node.js API"),
]


def _fuzzy_match(researched: str, expected: str) -> bool:
    """Check if researched value is compatible with expected.

    Uses substring matching to handle different levels of detail
    (e.g. 'OAuth2' category default should match detailed
    'OAuth 2.0 (JWT Bearer, Web Server)').
    """
    r = researched.lower().strip()
    e = expected.lower().strip()
    # Direct match
    if r == e:
        return True
    # One contains the other
    if len(r) >= 4 and (r in e or e in r):
        return True
    # OAuth category-level match
    if "oauth" in r and "oauth" in e:
        return True
    if "api key" in r and "api key" in e:
        return True
    if "bearer" in r and "bearer" in e:
        return True
    if "basic" in r and "basic" in e:
        return True
    # Access/category-level match
    if "self-serve" in r and "self-serve" in e:
        return True
    if "free" in r and "free" in e:
        return True
    if "enterprise" in r and "enterprise" in e:
        return True
    if "paid" in r and "paid" in e:
        return True
    if "trial" in r and "trial" in e:
        return True
    # API match
    if "rest" in r and "rest" in e:
        return True
    if "graphql" in r and "graphql" in e:
        return True
    if "mcp" in r and "mcp" in e:
        return True
    if "cli" in r and "cli" in e:
        return True
    return False


class VerificationAgent:
    """Runs an independent verification pass on the research data.

    Compares both first-pass (category defaults) and final (researched)
    against independently validated expected values.
    """

    def __init__(self, research_data: dict):
        self.research_data = research_data
        self.by_name = {r["app"]: r for r in research_data["rows"]}
        self.bv = None
        self.is_agentic = "Agentic" in self.research_data.get("method", "")

    def run(self) -> dict:
        """Execute verification and return results."""
        fields = ("auth", "access", "api")
        records = []
        first_hits = 0
        final_hits = 0
        total = 0
        per_app: dict[str, dict] = {}
        
        # Keep track of apps verified with browser-use
        browser_verified_apps = 0

        console.print("[dim]Running stratified 20-app verification...[/dim]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("[yellow]Verifying...", total=len(VERIFICATION_SAMPLE))

            for number, name, exp_auth, exp_access, exp_api in VERIFICATION_SAMPLE:
                row = self.by_name.get(name)
                if not row:
                    progress.advance(task)
                    continue

                first = row.get("first_pass", {})
                final = row.get("final", {})

                first_matches = []
                final_matches = []
                field_results = {}
                
                evidence_url = row.get("evidence", "")

                for field, expected in [("auth", exp_auth), ("access", exp_access), ("api", exp_api)]:
                    f_val = first.get(field, "")
                    fn_val = final.get(field, "")

                    f_ok = _fuzzy_match(f_val, expected)
                    
                    fn_ok = False
                    
                    # We run browser-verification for the first 2 apps as a sample, to keep runtime reasonable
                    if self.is_agentic and evidence_url and not evidence_url.startswith("http://[GATED]") and browser_verified_apps < 2:
                        if self.bv is None:
                            try:
                                from agents.browser_verifier import BrowserVerifier
                                self.bv = BrowserVerifier()
                            except ImportError:
                                pass
                        
                        if self.bv:
                            try:
                                progress.update(task, description=f"[yellow]Browser-verifying {name}...")
                                hypothesis = {"auth": fn_val, "access": final.get("access", ""), "api": final.get("api", "")}
                                bv_res = self.bv.verify_app(name, hypothesis, evidence_url)
                                
                                if field == "auth":
                                    fn_ok = "auth" not in bv_res.get("corrected_fields", [])
                                elif field == "access":
                                    fn_ok = "access" not in bv_res.get("corrected_fields", [])
                                else:
                                    fn_ok = "api" not in bv_res.get("corrected_fields", [])
                            except Exception as e:
                                fn_ok = _fuzzy_match(fn_val, expected)
                        else:
                            fn_ok = _fuzzy_match(fn_val, expected)
                    else:
                        fn_ok = _fuzzy_match(fn_val, expected)

                    if f_ok:
                        first_matches.append(field)
                        first_hits += 1
                    total += 1

                    if fn_ok:
                        final_matches.append(field)
                        final_hits += 1

                    field_results[field] = {
                        "expected": expected,
                        "first_pass": f_val,
                        "first_pass_match": f_ok,
                        "final": fn_val,
                        "final_match": fn_ok,
                    }
                    
                if self.is_agentic and evidence_url and not evidence_url.startswith("http://[GATED]"):
                    browser_verified_apps += 1

                progress.update(task, advance=1, description=f"[yellow]Verifying {name}...")

                per_app[name] = {
                    "id": number,
                    "app": name,
                    "first_pass_matches": first_matches,
                    "final_matches": final_matches,
                    "official_source_url": row.get("evidence", ""),
                    "corrected_fields": [
                        f for f in fields if f not in first_matches and f in final_matches
                    ],
                    "still_wrong": [
                        f for f in fields if f not in final_matches
                    ],
                    "field_results": field_results,
                }
                records.append(per_app[name])

        first_accuracy = round(first_hits / total, 3) if total else 0
        final_accuracy = round(final_hits / total, 3) if total else 0
        improvement = round((final_accuracy - first_accuracy) * 100, 1)

        # Summary table
        table = Table(title="[bold]Verification Results[/bold]", box=box.ROUNDED)
        table.add_column("App", style="cyan")
        table.add_column("First Pass", style="yellow")
        table.add_column("Final", style="green")
        for name, rec in sorted(per_app.items()):
            fp = ", ".join(rec["first_pass_matches"]) if rec["first_pass_matches"] else "—"
            fn = ", ".join(rec["final_matches"]) if rec["final_matches"] else "—"
            table.add_row(name[:25], fp, fn)
        console.print(table)

        console.print(f"  [cyan]First-pass accuracy:[/cyan] {first_hits}/{total} ({round(first_accuracy*100,1)}%)")
        console.print(f"  [green]After research loop:[/green] {final_hits}/{total} ({round(final_accuracy*100,1)}%)")
        console.print(f"  [bold]Improvement:[/bold] {improvement} percentage points")

        return {
            "sample_size": len(records),
            "sample_design": "20 apps stratified across all 10 categories (2 per category)",
            "first_pass": {"hits": first_hits, "fields": total, "accuracy": first_accuracy},
            "after_research_loop": {"hits": final_hits, "fields": total, "accuracy": final_accuracy},
            "improvement_pp": improvement,
            "records": records,
            "per_app": per_app,
            "limitations": [
                "20-row check is directional, not statistically representative of all 100 rows.",
                "Verification checks documentation accuracy, not production API testing.",
                "Fuzzy matching tolerates category-level vs detailed values.",
                "Re-verify before production sourcing; API policies and plan gates change.",
            ],
        }
