"""Pydantic models for the research pipeline."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Any

from pydantic import BaseModel, Field


class Confidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class AuthMethod(str, Enum):
    OAUTH2 = "OAuth2"
    API_KEY = "API Key"
    BASIC = "Basic Auth"
    BEARER_TOKEN = "Bearer Token"
    JWT = "JWT"
    NONE = "None"
    OTHER = "Other"


class AccessType(str, Enum):
    SELF_SERVE = "Self-serve"
    FREE_TIER = "Free tier"
    TRIAL = "Trial"
    PAID_PLAN = "Paid plan"
    ADMIN_APPROVAL = "Admin approval"
    ENTERPRISE_GATE = "Enterprise gate"
    PARTNERSHIP_GATE = "Partnership gate"
    CONTACT_SALES = "Contact sales"
    UNKNOWN = "Unknown"


class AppResearch(BaseModel):
    """Complete research output for one application."""

    id: int
    app: str
    category: str
    description: str = ""
    auth_methods: list[AuthMethod] = []
    access_type: AccessType = AccessType.UNKNOWN
    access_detail: str = ""
    has_rest: bool = False
    has_graphql: bool = False
    has_sdk: bool = False
    api_breadth: str = ""
    has_mcp: bool = False
    mcp_detail: str = ""
    buildability: str = ""
    primary_blocker: str = ""
    composio_supported: bool = False
    composio_tools: int = 0
    composio_managed_auth: bool = False
    composio_demand_rank: Optional[int] = None
    evidence_urls: list[str] = []
    confidence: Confidence = Confidence.LOW
    needs_review: bool = True
    source_note: str = ""

    def dict(self, *args, **kwargs):
        d = super().dict(*args, **kwargs)
        d["confidence"] = self.confidence.value
        d["auth_methods"] = [a.value for a in self.auth_methods]
        d["access_type"] = self.access_type.value
        return d


class VerificationResult(BaseModel):
    """Result of a verification pass against an app."""

    app: str
    field: str
    first_pass_value: str
    verified_value: str
    match: bool
    evidence_url: str


class AppRecord(BaseModel):
    """Persistent record for one app in the database."""

    id: int
    app: str
    category: str
    description: str = ""
    auth: str = ""
    access: str = ""
    api: str = ""
    mcp: str = ""
    verdict: str = ""
    evidence: str = ""
    evidence_grade: str = ""
    confidence: str = "LOW"
    needs_review: bool = True
    composio_supported: Any = False
    composio_tools: Any = 0
    composio_managed_auth: Any = False
    composio_demand_rank: Optional[int] = None
    first_pass_auth: str = ""
    first_pass_access: str = ""
    first_pass_api: str = ""
    first_pass_verdict: str = ""
    source_note: str = ""
    created_at: str = ""


class BatchResult(BaseModel):
    """Full pipeline output."""

    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    method: str = ""
    total_apps: int = 0
    researched: int = 0
    verified: int = 0
    high_confidence: int = 0
    medium_confidence: int = 0
    low_confidence: int = 0
    needs_review: int = 0
    rows: list[AppRecord] = []
    stats: dict = {}
    insights: dict = {}
    verification: dict = {}
