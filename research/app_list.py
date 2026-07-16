"""The master list of 100 apps organised by category."""

from __future__ import annotations


def all_apps() -> list[dict]:
    """Return the full 100-app research set with one-line descriptions."""
    rows: list[dict] = []

    def add(cat: str, entries: list[tuple[str, str, str]]):
        start = len(rows) + 1
        for offset, (name, hint, desc) in enumerate(entries):
            rows.append({"id": start + offset, "app": name, "category": cat, "hint": hint, "description": desc})

    add("CRM & Sales", [
        ("Salesforce", "salesforce.com", "Enterprise CRM with 9 API families and free dev edition"),
        ("HubSpot", "hubspot.com", "CRM, marketing, sales, and CMS platform with free dev test account"),
        ("Pipedrive", "pipedrive.com", "Sales pipeline CRM with REST API and free developer sandbox"),
        ("Attio", "attio.com", "AI-native CRM with MCP server and free plan API access"),
        ("Twenty", "twenty.com (open-source CRM)", "Open-source CRM with REST, GraphQL, and native MCP endpoint"),
        ("Podio", "podio.com", "Workflow and collaboration platform (Citrix-owned, maintenance mode)"),
        ("Zoho CRM", "zoho.com/crm", "CRM with REST API and free edition (3 users, 250 calls/day)"),
        ("Close", "close.com", "Sales engagement CRM with REST API and 14-day free trial"),
        ("Copper", "copper.com", "CRM with REST API gated behind $59/user/mo Professional plan"),
        ("DealCloud", "api.docs.dealcloud.com", "Enterprise deal management CRM ($85K+/yr, no self-serve)"),
    ])
    add("Support & Helpdesk", [
        ("Zendesk", "zendesk.com", "Customer support platform with very broad REST API and 452 Composio tools"),
        ("Intercom", "intercom.com", "Customer messaging platform with REST API and free dev workspace"),
        ("Freshdesk", "freshdesk.com", "Helpdesk with REST API v2 and simple API key auth"),
        ("Front", "front.com", "Shared inbox platform with REST API and free developer account"),
        ("Pylon", "usepylon.com", "B2B customer success platform with REST API (paid-only)"),
        ("LiveAgent", "liveagent.com", "Helpdesk with REST API v3 and 14-day free trial"),
        ("Plain", "plain.com", "API-first customer support with GraphQL, MCP, and 7-day trial"),
        ("Help Scout", "helpscout.com", "Customer support with Mailbox REST API + Docs API"),
        ("Gorgias", "gorgias.com", "E-commerce helpdesk with REST API and sandbox for public apps"),
        ("Gladly", "gladly.com", "Customer service platform with REST API (sandbox needs sales)"),
    ])
    add("Communications & Messaging", [
        ("Slack", "slack.com", "Team messaging with 150+ REST methods and Socket Mode"),
        ("Twilio", "twilio.com", "CPaaS with REST APIs for SMS, Voice, Video, and $15 free credit"),
        ("Zoho Cliq", "zoho.com/cliq", "Team collaboration with REST API, bot framework, and free tier"),
        ("Lark (Larksuite)", "open.larksuite.com", "All-in-one collaboration with 2500+ APIs and official MCP"),
        ("Pumble", "pumble.com", "Team chat with REST API and free tier (unlimited users)"),
        ("Discord", "discord.com", "Chat platform with REST + WebSocket Gateway and free bot dev"),
        ("Telegram", "core.telegram.org", "Messaging with 60+ bot API methods and completely free"),
        ("WhatsApp Business", "developers.facebook.com/docs/whatsapp", "Business messaging via Meta Graph API with test tier"),
        ("Aircall", "aircall.io", "Cloud phone system with REST API (paid subscription required)"),
        ("Vonage", "developer.vonage.com", "CPaaS with SMS, Voice, Verify APIs and free trial credit"),
    ])
    add("Marketing, Ads, Email & Social", [
        ("Google Ads", "developers.google.com/google-ads", "Ad platform with REST+gRPC API and developer token approval gate"),
        ("Meta Ads", "developers.facebook.com/docs/marketing-apis", "Social ads via Meta Graph API with App Review gate"),
        ("LinkedIn Ads", "learn.microsoft.com/linkedin/marketing", "B2B ad platform with OAuth and 4-week+ manual approval"),
        ("GoHighLevel", "highlevel.stoplight.io", "Marketing automation platform with self-serve REST API"),
        ("Mailchimp", "mailchimp.com/developer", "Email marketing with REST v3 API and free tier"),
        ("Klaviyo", "developers.klaviyo.com", "E-commerce marketing with JSON:API and mandatory OAuth 2.0"),
        ("systeme.io", "systeme.io (funnel builder)", "Funnel builder with REST API, MCP server, and free tier"),
        ("Pinterest", "developers.pinterest.com", "Visual discovery with REST v5 API and manual access review"),
        ("Threads (Meta)", "developers.facebook.com/docs/threads", "Text-first social via Meta Graph API (narrow, testers mode)"),
        ("SendGrid", "sendgrid.com", "Email delivery with REST v3 API and free 100 emails/day"),
    ])
    add("Ecommerce", [
        ("Shopify", "shopify.dev", "E-commerce platform with GraphQL API and free development stores"),
        ("WooCommerce", "woocommerce.com/document/woocommerce-rest-api", "WordPress e-commerce plugin with REST API v3"),
        ("BigCommerce", "developer.bigcommerce.com", "E-commerce with REST + GraphQL APIs and free trial stores"),
        ("Salesforce Commerce Cloud", "developer.salesforce.com/docs/commerce", "Enterprise commerce with SLAS OAuth 2.1 (license required)"),
        ("Magento (Adobe Commerce)", "developer.adobe.com/commerce", "E-commerce platform with REST + GraphQL (free OSS version)"),
        ("Squarespace", "developers.squarespace.com", "Website builder with Commerce APIs (paid plan required)"),
        ("Ecwid", "api-docs.ecwid.com", "E-commerce widget with REST v3 API and free development store"),
        ("Gumroad", "gumroad.com/api", "Digital product sales with REST v2 and simple OAuth"),
        ("Amazon Selling Partner", "developer-docs.amazon.com/sp-api", "Amazon marketplace API with complex multi-step auth (LWA+SigV4+RDT)"),
        ("fanbasis", "fanbasis.com", "Creator commerce with REST API and self-serve API keys"),
    ])
    add("Data, SEO & Scraping", [
        ("DataForSEO", "docs.dataforseo.com", "SEO data API with pay-as-you-go pricing and MCP server"),
        ("SE Ranking", "seranking.com/api", "SEO platform with OpenAPI 3.0 spec and free trial"),
        ("Ahrefs", "ahrefs.com/api", "SEO analytics with REST API (Enterprise plan for direct access)"),
        ("MrScraper", "docs.mrscraper.com", "AI web scraper with REST API and free tier"),
        ("Apify", "docs.apify.com", "Web scraping platform with MCP, SDKs in 7 languages, free $5 tier"),
        ("Firecrawl", "firecrawl.dev", "AI web crawler with MCP, open-source, 1000 free credits/mo"),
        ("Bright Data", "brightdata.com", "Proxy and web scraping platform with pay-as-you-go pricing"),
        ("Sherlock", "github.com/sherlock-project/sherlock", "Username enumeration CLI across 400+ social networks (open-source)"),
        ("Waterfall.io", "waterfall.io (contact/company intel)", "B2B contact and company intelligence with OpenAPI 3.1"),
        ("Clay", "clay.com", "Sales enrichment with MCP server (full API enterprise-only)"),
    ])
    add("Developer, Infra & Data Platforms", [
        ("GitHub", "docs.github.com/rest", "Source control with REST + GraphQL, free tier, and 893 Composio tools"),
        ("Vercel", "vercel.com/docs/rest-api", "Frontend deployment with REST API and free Hobby plan"),
        ("Netlify", "docs.netlify.com/api", "Web hosting with REST API and free tier (100GB bandwidth)"),
        ("Cloudflare", "developers.cloudflare.com/api", "Edge network with 100+ product APIs and generous free tier"),
        ("Supabase", "supabase.com/docs", "Open-source Firebase alternative with auto-generated REST API"),
        ("Neo4j", "neo4j.com/docs/api", "Graph database with AuraDB REST API and free tier"),
        ("Snowflake", "docs.snowflake.com", "Cloud data warehouse with SQL REST API and free trial"),
        ("MongoDB Atlas", "mongodb.com/docs/atlas/api", "Managed MongoDB with admin REST API and free M0 cluster"),
        ("Datadog", "docs.datadoghq.com/api", "Monitoring platform with very broad REST API and free tier"),
        ("Sentry", "docs.sentry.io/api", "Error tracking with REST API and free 5K events/month"),
    ])
    add("Productivity & Project Management", [
        ("Notion", "developers.notion.com", "Docs and project management with REST API and 45 Composio tools"),
        ("Airtable", "airtable.com/developers", "Spreadsheet-database hybrid with REST API and free tier"),
        ("Linear", "developers.linear.app", "Issue tracking with comprehensive GraphQL API and free tier"),
        ("Jira", "developer.atlassian.com", "Project management with REST API and cloud free tier"),
        ("Asana", "developers.asana.com", "Work management with REST API, MCP, and free tier"),
        ("Monday.com", "developer.monday.com", "Work OS with GraphQL API, MCP (50+ tools), free dev account"),
        ("ClickUp", "clickup.com/api", "All-in-one productivity with REST API, MCP, and 164 Composio tools"),
        ("Coda", "coda.io/developers", "Docs platform with REST API v1 and free tier"),
        ("Smartsheet", "smartsheet.com/developers", "Spreadsheet-collaboration with REST API, MCP (paid plan required)"),
        ("Harvest", "harvestapp.com (help.getharvest.com/api-v2)", "Time tracking with REST v2 and 30-day free trial"),
    ])
    add("Finance & Fintech", [
        ("Stripe", "stripe.com/docs/api", "Payment processing with 300+ endpoints, free test mode, 422 Composio tools"),
        ("Plaid", "plaid.com/docs", "Financial data aggregation with free Sandbox and trial plan"),
        ("Binance", "binance-docs.github.io", "Crypto exchange with REST + WebSocket APIs and self-serve keys"),
        ("Paygent Connect", "paygent (NMI-powered)", "Payment gateway via NMI with REST API (merchant account required)"),
        ("iPayX", "ipayx.ai/docs", "FX audit and forensic reporting with MCP-only interface"),
        ("QuickBooks", "developer.intuit.com", "Accounting with REST + GraphQL, free sandbox with test company"),
        ("Xero", "developer.xero.com", "Accounting with 237 REST endpoints and free demo company"),
        ("Brex", "developer.brex.com", "Expense management with REST API and self-serve user tokens"),
        ("Ramp", "docs.ramp.com", "Spend management with MCP, Agent Cards, and self-serve admin access"),
        ("PitchBook", "pitchbook.com (research API)", "Private market data with REST API (enterprise contract required)"),
    ])
    add("AI, Research & Media-native", [
        ("NotebookLM", "cloud.google.com/gemini (Enterprise API)", "Google AI notebook with Discovery Engine API (enterprise-only)"),
        ("Otter AI", "help.otter.ai (MCP server)", "Meeting transcription with MCP server (3 tools) and enterprise-gated REST"),
        ("Fathom", "fathom.video", "Meeting transcription and summaries with REST API and free tier"),
        ("Consensus", "consensus.app (OAuth requested)", "Research paper search with single-endpoint REST and MCP server"),
        ("Reducto", "reducto.ai (document parsing)", "Document parsing with REST API, free account, and SDKs in 3 languages"),
        ("Devin", "docs.devin.ai (MCP)", "AI software engineer with native MCP, REST, and CLI access"),
        ("higgsfield", "higgsfield.ai/cli (content suite)", "AI content suite with CLI, Python SDK, and DataDome-protected REST"),
        ("Mermaid CLI", "github.com/mermaid-js/mermaid-cli", "Diagram generation CLI (Node.js, no auth, open-source MIT)"),
        ("YouTube Transcript", "transcriptapi.com", "YouTube transcript and search API with MCP and credit-based pricing"),
        ("Grain", "grain.com (meeting notes)", "Meeting recording and highlights with REST v2 API and MCP"),
    ])
    return rows
