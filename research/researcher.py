"""Core research logic that classifies apps using the researched dataset."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Optional

from research.app_list import all_apps
from research.dataset import RESEARCHED


CATEGORY_DEFAULTS = {
    "CRM & Sales": {"auth": "OAuth2", "access": "Self-serve trial", "api": "REST"},
    "Support & Helpdesk": {"auth": "OAuth2 / API token", "access": "Self-serve trial", "api": "REST"},
    "Communications & Messaging": {"auth": "OAuth2, bot token", "access": "Mostly self-serve", "api": "REST"},
    "Marketing, Ads, Email & Social": {"auth": "OAuth2", "access": "Self-serve developer account", "api": "REST/Graph APIs"},
    "Ecommerce": {"auth": "API key/secret, OAuth2", "access": "Self-serve sandbox", "api": "REST/GraphQL"},
    "Data, SEO & Scraping": {"auth": "API key or bearer token", "access": "Self-serve signup/trial", "api": "REST"},
    "Developer, Infra & Data Platforms": {"auth": "Personal/API token", "access": "Self-serve", "api": "REST"},
    "Productivity & Project Management": {"auth": "OAuth2", "access": "Usually self-serve", "api": "REST/GraphQL"},
    "Finance & Fintech": {"auth": "OAuth2, API key", "access": "Paid, compliance", "api": "REST"},
    "AI, Research & Media-native": {"auth": "API key, OAuth2", "access": "Self-serve trial", "api": "REST/CLI/MCP mix"},
}

COMPOSIO_DEMAND = {
    "Slack": 5, "HubSpot": 6, "GitHub": 8, "Airtable": 10, "Notion": 11,
    "ClickUp": 12, "Linear": 14, "Asana": 15, "Salesforce": 16, "Stripe": 17,
    "Shopify": 18, "Jira": 19, "Monday.com": 21, "Intercom": 22, "Zendesk": 23,
    "Discord": 25,
}


def source_url(hint: str) -> str:
    match = re.search(r"([a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^ ]*)?)", hint)
    if not match:
        return ""
    return "https://" + match.group(1).rstrip(").,")


def resolve_confidence(app_name: str) -> str:
    """Assign confidence based on researched data quality."""
    if app_name in RESEARCHED:
        return "HIGH"
    return "LOW"


def needs_review(app_name: str) -> bool:
    """App needs human review if not in researched dataset."""
    return app_name not in RESEARCHED


def build_verdict(auth: str, access: str, api: str) -> str:
    """Derive a buildability verdict from the research fields."""
    verdict = "High potential"
    blocker = ""
    access_lower = access.lower()

    if any(w in access_lower for w in ["enterprise gate", "contact sales", "no self-serve"]):
        verdict = "Low potential"
        blocker = "Enterprise gate / sales-led access"
    elif any(w in access_lower for w in ["paid plan required", "paid.*only", "gated"]):
        verdict = "Medium potential"
        blocker = "Paid plan or admin approval required"
    elif any(w in access_lower for w in ["compliance", "review", "approval"]) and "self" not in access_lower:
        verdict = "Medium potential"
        blocker = "Compliance / review gate"
    elif any(w in access_lower for w in ["trial", "limit"]):
        if "free" not in access_lower:
            verdict = "Medium potential"
            blocker = "Limited free tier"
    else:
        verdict = "High potential"

    if "narrow" in api.lower():
        verdict = "Medium potential"
        blocker = "Narrow API surface"

    if verdict == "High potential":
        blocker = "None"

    return f"{verdict}: {blocker}"


def research_all(live_check: bool = False, agentic: bool = False, limit: int = 100, progress_callback=None) -> dict:
    """Run the full research pass across all apps."""
    
    agent = None
    if agentic:
        try:
            from intelligence.agentic import AgenticResearcher
            agent = AgenticResearcher()
        except Exception as e:
            from rich.console import Console
            Console().print(f"[red]Failed to initialize AgenticResearcher: {e}[/red]")
            agent = None

    import httpx
    import concurrent.futures

    def process_app(app):
        defaults = CATEGORY_DEFAULTS.get(app["category"], {})
        researched = RESEARCHED.get(app["app"])

        first_pass = {
            "auth": defaults.get("auth", ""),
            "access": defaults.get("access", ""),
            "api": defaults.get("api", ""),
            "verdict": "Toolkit candidate; validate access",
        }

        if agent:
            # Force LLM research if agent is active (ignore cache)
            agent_data = agent.research_app(app["app"], source_url(app["hint"]))
            if agent_data:
                final = {
                    "auth": agent_data["auth"],
                    "access": agent_data["access"],
                    "api": agent_data["api"],
                    "verdict": agent_data["verdict"],
                }
                ev_url = agent_data["evidence"]
                mcp = ""
                confidence = "HIGH"
                human_follow_up = False
                evidence_grade = "high"
                source_note = "Web-researched via Agentic Pipeline with OpenRouter and Composio MCP"
            else:
                final = {**first_pass}
                ev_url = source_url(app["hint"])
                mcp = ""
                confidence = "LOW"
                human_follow_up = True
                evidence_grade = "medium"
                source_note = "Agent failed; category default applied"
        elif researched:
            ev_url = "https://" + researched.get("evidence_slug", "")
            final = {
                "auth": researched["auth"],
                "access": researched["access"],
                "api": researched["api"],
                "verdict": researched["verdict"],
            }
            mcp = researched.get("mcp", "")
            confidence = "HIGH"
            human_follow_up = False
            evidence_grade = "high"
            source_note = "Web-researched: official developer documentation verified"
        else:
            final = {**first_pass}
            ev_url = source_url(app["hint"])
            mcp = ""
            confidence = "LOW"
            human_follow_up = True
            evidence_grade = "medium"
            source_note = "Not yet researched; category default applied"

        if live_check and ev_url and "[GATED]" not in ev_url:
            try:
                with httpx.Client(follow_redirects=True, timeout=5.0) as client:
                    resp = client.get(ev_url, headers={"User-Agent": "Mozilla/5.0"})
                    if resp.status_code >= 400:
                        source_note += f" [URL Check Failed: {resp.status_code}]"
            except Exception as e:
                source_note += f" [URL Check Failed: Error]"
        
        if ev_url:
            ev_url = ev_url.replace("https://[GATED] ", "https://").replace("[GATED] ", "")

        from services.composio_client import composio as _composio_cli
        _composio_cli._ensure_init()
        _tk = _composio_cli.check_toolkit(app["app"])
        _composio_supported = _tk.get("supported", False) if isinstance(_tk, dict) else (app["app"] in COMPOSIO_DEMAND)
        _composio_tools = _tk.get("tools", 0) if isinstance(_tk, dict) else 0
        _composio_managed = _tk.get("managed_auth", False) if isinstance(_tk, dict) else False

        return {
            **app,
            "description": app.get("description", ""),
            "auth": final["auth"],
            "access": final["access"],
            "api": final["api"],
            "mcp": mcp,
            "verdict": final["verdict"],
            "evidence": ev_url,
            "evidence_grade": evidence_grade,
            "source_note": source_note,
            "confidence": confidence,
            "first_pass": first_pass,
            "final": final,
            "human_follow_up": human_follow_up,
            "composio_demand_rank": COMPOSIO_DEMAND.get(app["app"]),
            "composio_supported": _composio_supported,
            "composio_tools": _composio_tools,
            "composio_managed_auth": _composio_managed,
        }

    apps_to_process = list(all_apps())[:limit]
    rows = []
    
    if agent:
        # Run concurrently for speed
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(process_app, app): app for app in apps_to_process}
            for future in concurrent.futures.as_completed(futures):
                rows.append(future.result())
                if progress_callback:
                    progress_callback()
    else:
        # Sequential is fine for deterministic
        for app in apps_to_process:
            rows.append(process_app(app))
            if progress_callback:
                progress_callback()

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "method": "Deterministic research pipeline with web-researched dataset" if not agent else "Agentic research pipeline",
        "live_check": live_check,
        "rows": rows,
        "stats": compute_stats(rows),
    }


def compute_stats(rows: list[dict]) -> dict:
    from collections import Counter
    auth_counter = Counter()
    for r in rows:
        a = r.get("auth", "")
        if "OAuth" in a:
            auth_counter["OAuth2"] += 1
        elif "API key" in a.lower() or "api key" in a.lower():
            auth_counter["API key"] += 1
        elif "bearer" in a.lower() or "token" in a.lower():
            auth_counter["Bearer token"] += 1
        elif "basic" in a.lower():
            auth_counter["Basic Auth"] += 1
        else:
            auth_counter["Other"] += 1

    confidence_counts = Counter(r.get("confidence", "LOW") for r in rows)

    return {
        "total": len(rows),
        "categories": dict(Counter(r["category"] for r in rows)),
        "auth_families": dict(auth_counter),
        "confidence": dict(confidence_counts),
        "high_confidence": confidence_counts.get("HIGH", 0),
        "medium_confidence": confidence_counts.get("MEDIUM", 0),
        "low_confidence": confidence_counts.get("LOW", 0),
        "mcp_count": sum(1 for r in rows if r.get("mcp") and "mcp" in r["mcp"].lower() and "no" not in r["mcp"].lower()),
        "researched": sum(1 for r in rows if not r["human_follow_up"]),
        "needs_review": sum(1 for r in rows if r["human_follow_up"]),
        "composio_supported": sum(1 for r in rows if isinstance(r.get("composio_supported"), bool) and r.get("composio_supported")),
        "composio_total_tools": sum(r.get("composio_tools", 0) for r in rows if isinstance(r.get("composio_tools", 0), (int, float))),
        "composio_managed_auth_count": sum(1 for r in rows if isinstance(r.get("composio_managed_auth"), bool) and r.get("composio_managed_auth")),
    }
