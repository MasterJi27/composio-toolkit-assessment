"""Centralised configuration loaded from environment variables."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Composio
    composio_api_key: str = ""
    composio_project_id: str = "default"
    composio_org_id: str = "default"
    composio_user_id: str = "default"
    composio_user_email: str = "agent@composio.dev"
    openai_api_key: str = ""
    gemini_api_key: str = ""

    # Research mode
    research_mode: Literal["composio", "deterministic", "ai"] = "deterministic"
    live_check: bool = False

    # Output
    data_dir: Path = ROOT / "data"
    report_dir: Path = ROOT / "frontend"

    @property
    def composio_configured(self) -> bool:
        return bool(self.composio_api_key)

    @property
    def research_json(self) -> Path:
        return self.data_dir / "research.json"

    @property
    def verification_json(self) -> Path:
        return self.data_dir / "verification.json"

    @property
    def db_path(self) -> Path:
        return self.data_dir / "research.db"


settings = Settings()
