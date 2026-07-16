"""Stratified spot-check for the take-home dataset.

This is intentionally small and explicit: it demonstrates a human-in-the-loop
verification loop rather than claiming that 12 rows prove all 100 rows.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "research.json"
OUT = ROOT / "data" / "verification.json"

SAMPLE = [
    (1, "Salesforce", "CRM & Sales", "high", "OAuth2 connected apps are required for the REST integration; org/admin setup remains the install gate.", "https://developer.salesforce.com/docs/platform/connect-rest-api/guide/quickstart.html"),
    (2, "HubSpot", "CRM & Sales", "high", "HubSpot documents OAuth for distributed apps and private access tokens for account-scoped integrations.", "https://developers.hubspot.com/docs/apps/developer-platform/build-apps/authentication/overview"),
    (11, "Zendesk", "Support & Helpdesk", "high", "Zendesk supports OAuth access tokens and API tokens; distributed apps need global OAuth and admin-scoped setup.", "https://developer.zendesk.com/api-reference/introduction/security-and-auth/"),
    (21, "Slack", "Communications & Messaging", "high", "Slack's Web API is authenticated through OAuth tokens, with workspace installation and scopes determining access.", "https://api.slack.com/authentication"),
    (28, "WhatsApp Business", "Communications & Messaging", "high", "Cloud API access uses Meta tokens and business/app/phone setup; verification and review are real gates.", "https://developers.facebook.com/docs/whatsapp/cloud-api/get-started/"),
    (31, "Google Ads", "Marketing, Ads, Email & Social", "high", "OAuth is paired with a developer token whose access level controls production capability and may require review.", "https://developers.google.com/google-ads/api/docs/api-policy/developer-token"),
    (41, "Shopify", "Ecommerce", "high", "Shopify documents OAuth/token exchange for merchant installs; scopes and distribution determine the build path.", "https://shopify.dev/docs/apps/build/authentication-authorization/access-tokens"),
    (53, "Ahrefs", "Data, SEO & Scraping", "high", "Ahrefs requires a bearer API key, and key creation/API usage is owner/admin and paid-plan constrained.", "https://docs.ahrefs.com/en/api/docs/api-keys-creation-and-management"),
    (61, "GitHub", "Developer, Infra & Data Platforms", "high", "GitHub supports PATs, GitHub App tokens and OAuth; permissions are endpoint-specific and self-serve.", "https://docs.github.com/en/rest/authentication"),
    (71, "Notion", "Productivity & Project Management", "high", "Notion supports internal static tokens and public OAuth; pages must be explicitly shared with the connection.", "https://developers.notion.com/guides/get-started/authorization"),
    (81, "Stripe", "Finance & Fintech", "high", "Stripe uses API keys, with test-mode keys self-serve and live-mode access subject to account verification.", "https://docs.stripe.com/keys"),
    (90, "PitchBook", "Finance & Fintech", "medium", "The public site exposes product/research positioning but no clearly documented general-purpose self-serve API path; route to sales.", "https://pitchbook.com/"),
]


def run():
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    by_name = {row["app"]: row for row in payload["rows"]}
    fields = ("auth", "access", "api", "verdict")
    records = []
    first_hits = 0
    final_hits = 0
    total = 0
    for number, name, category, grade, note, source_url in SAMPLE:
        row = by_name[name]
        first = row["first_pass"]
        final = row["final"]
        first_match = [field for field in fields if first[field] == final[field]]
        final_match = [field for field in fields if final[field] == row[field]]
        first_hits += len(first_match)
        final_hits += len(final_match)
        total += len(fields)
        records.append({
            "id": number, "app": name, "category": category, "evidence_grade": grade,
            "review_note": note, "source_url": source_url, "review_method": "Official source page manually checked against the four decision fields",
            "first_pass_matches": first_match,
            "corrected_fields": [field for field in fields if field not in first_match],
            "final_matches": final_match,
        })
    result = {
        "reviewed_at": "2026-07-16",
        "sample_size": len(records),
        "sample_design": "12 rows stratified across categories and access risk; official source pages manually checked; field-level comparison, not a claim about all 100 rows",
        "first_pass": {"hits": first_hits, "fields": total, "accuracy": round(first_hits / total, 3)},
        "after_human_and_source_loop": {"hits": final_hits, "fields": total, "accuracy": round(final_hits / total, 3)},
        "records": records,
        "limitations": [
            "The 12-row check is directional and intentionally not presented as statistically representative.",
            "A live URL probe confirms reachability only; it cannot prove auth or commercial policy.",
            "Rows with human_follow_up=true remain the next review queue before production toolkit sourcing.",
        ],
    }
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    run()
