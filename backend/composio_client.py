"""Composio SDK wrapper for toolkit discovery, MCP, and managed auth."""

from __future__ import annotations

import os
from typing import Any, Optional

from backend.config import settings


class ComposioClient:
    """Wraps the Composio SDK for toolkit discovery and comparison.

    Uses:
    - composio.client for MCP/toolkit listing
    - composio.Composio for managed auth and tool execution
    """

    _instance: Optional["ComposioClient"] = None

    def __new__(cls) -> "ComposioClient":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
            cls._instance._client = None
            cls._instance._composio = None
            cls._instance._apps_cache = None
            cls._instance._mcp_cache = None
            cls._instance._accounts_cache = None
        return cls._instance

    def _ensure_init(self):
        if self._initialized:
            return
        if not settings.composio_configured:
            self._initialized = True
            return
        os.environ.setdefault("COMPOSIO_API_KEY", settings.composio_api_key)
        os.environ.setdefault("COMPOSIO_PROJECT_ID", settings.composio_project_id)
        os.environ.setdefault("COMPOSIO_ORG_ID", settings.composio_org_id)
        os.environ.setdefault("COMPOSIO_USER_ID", settings.composio_user_id)
        os.environ.setdefault("COMPOSIO_USER_EMAIL", settings.composio_user_email)
        try:
            from composio import Composio
            self._composio = Composio()
            self._client = self._composio.client
            self._apps_cache = None
            self._mcp_cache = None
            self._accounts_cache = None
            self._initialized = True
        except ImportError:
            self._initialized = True

    @property
    def available(self) -> bool:
        return settings.composio_configured

    def discover_apps(self) -> list[dict]:
        """Discover all apps/tools available through Composio's SDK.

        Returns list of {appName, description, authScheme, toolCount}.
        """
        self._ensure_init()
        if not self._client:
            return []
        try:
            if self._apps_cache is None:
                toolkits = self._client.toolkits.list()
                self._apps_cache = getattr(toolkits, "items", []) or []
            apps = self._apps_cache
            result = []
            for app in apps:
                try:
                    meta = getattr(app, "meta", None)
                    desc = getattr(meta, "description", "") if meta else ""
                    t_count = getattr(meta, "tools_count", 0) if meta else 0
                    auth = getattr(app, "auth_schemes", []) or []
                    auth_str = ", ".join(auth) if isinstance(auth, list) else str(auth)
                    result.append({
                        "appName": getattr(app, "name", str(app)),
                        "description": desc,
                        "authScheme": auth_str,
                        "toolCount": int(t_count) if t_count else 0,
                        "status": "native",
                    })
                except Exception:
                    result.append({"appName": str(app), "description": "", "authScheme": "", "toolCount": 0})
            return result
        except Exception as exc:
            return []

    def check_toolkit(self, app_name: str) -> dict:
        """Check if Composio already supports this app as a toolkit.

        Uses SDK's app lookup when available. Falls back to known-supported list.
        Always returns a dict with supported/tools/managed_auth.
        """
        self._ensure_init()

        slug = app_name.lower().replace(" ", "-").replace("(", "").replace(")", "").replace("/", "-")
        slug = slug.replace("--", "-").strip("-")

        # Try SDK app lookup if client is available
        if self._client:
            try:
                if self._apps_cache is None:
                    toolkits = self._client.toolkits.list()
                    self._apps_cache = getattr(toolkits, "items", []) or []
                apps = self._apps_cache
                for app in apps:
                    a_name = (getattr(app, "name", "") or "").lower()
                    a_slug = (getattr(app, "slug", "") or "").lower()
                    if slug == a_name or slug == a_slug or slug in a_name or a_name in slug or slug in a_slug or a_slug in slug:
                        meta = getattr(app, "meta", None)
                        tool_count = getattr(meta, "tools_count", 0) if meta else 0
                        auth = getattr(app, "auth_schemes", []) or []
                        return {
                            "supported": True,
                            "tools": int(tool_count) if tool_count else 0,
                            "managed_auth": bool(getattr(app, "composio_managed_auth_schemes", [])),
                            "auth_scheme": ", ".join(auth) if isinstance(auth, list) else str(auth),
                        }
            except Exception:
                pass

        # If we reach here, we didn't find it or SDK failed
        if not self._client:
            return {"supported": "Unavailable", "tools": "Unavailable", "managed_auth": "Unavailable"}
        return {"supported": False, "tools": 0, "managed_auth": False}

    def check_mcp(self, app_name: str) -> list[dict]:
        """Check if Composio offers MCP tools for this app."""
        self._ensure_init()
        if not self._client:
            return []

        slug = app_name.lower().replace(" ", "-").replace("(", "").replace(")", "").replace("/", "-")
        slug = slug.replace("--", "-").strip("-")

        try:
            if self._mcp_cache is None:
                self._mcp_cache = self._client.mcp.list()
            mcp_list = self._mcp_cache
            results = []
            for item in (mcp_list.items or []):
                item_name = (getattr(item, "name", "") or "").lower()
                if slug in item_name or item_name in slug:
                    results.append({
                        "name": getattr(item, "name", ""),
                        "description": getattr(item, "description", ""),
                        "tools": getattr(item, "tools", 0),
                    })
            return results
        except Exception:
            return []

    def get_connected_accounts(self) -> list[dict]:
        """List all connected accounts in the current Composio project."""
        self._ensure_init()
        if not self._client:
            return []
        try:
            if self._accounts_cache is None:
                self._accounts_cache = self._client.connected_accounts.list()
            accounts = self._accounts_cache
            return [
                {
                    "id": getattr(a, "id", ""),
                    "app": getattr(a, "appUniqueId", ""),
                    "status": getattr(a, "status", ""),
                    "createdAt": getattr(a, "createdAt", ""),
                }
                for a in (accounts or [])
            ]
        except Exception:
            return []

    def get_demand_rank(self, app_name: str) -> Optional[int]:
        """Return Composio demand rank from known top-25 list."""
        demand = {
            "Slack": 5, "HubSpot": 6, "GitHub": 8, "Airtable": 10, "Notion": 11,
            "ClickUp": 12, "Linear": 14, "Asana": 15, "Salesforce": 16, "Stripe": 17,
            "Shopify": 18, "Jira": 19, "Monday.com": 21, "Intercom": 22, "Zendesk": 23,
            "Discord": 25,
        }
        return demand.get(app_name)


composio = ComposioClient()
