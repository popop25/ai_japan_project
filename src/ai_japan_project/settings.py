from __future__ import annotations

import os
from enum import Enum

from pydantic import BaseModel


class AppMode(str, Enum):
    LOCAL = "local"
    ATLASSIAN = "atlassian"


class AppSettings(BaseModel):
    mode: AppMode = AppMode.LOCAL
    atlassian_email: str | None = None
    atlassian_api_token: str | None = None
    jira_base_url: str | None = None
    jira_project_key: str | None = None
    confluence_base_url: str | None = None
    confluence_space_key: str | None = None
    confluence_context_parent_id: str | None = None
    confluence_artifacts_parent_id: str | None = None

    @classmethod
    def from_env(cls) -> "AppSettings":
        return cls(
            mode=AppMode(os.getenv("AJP_MODE", AppMode.LOCAL.value)),
            atlassian_email=os.getenv("ATLASSIAN_EMAIL"),
            atlassian_api_token=os.getenv("ATLASSIAN_API_TOKEN"),
            jira_base_url=_normalize_base_url(os.getenv("JIRA_BASE_URL")),
            jira_project_key=os.getenv("JIRA_PROJECT_KEY"),
            confluence_base_url=_normalize_base_url(os.getenv("CONFLUENCE_BASE_URL")),
            confluence_space_key=os.getenv("CONFLUENCE_SPACE_KEY"),
            confluence_context_parent_id=os.getenv("CONFLUENCE_CONTEXT_PARENT_ID"),
            confluence_artifacts_parent_id=os.getenv("CONFLUENCE_ARTIFACTS_PARENT_ID"),
        )

    def validate_atlassian(self) -> None:
        missing = [
            name
            for name, value in [
                ("ATLASSIAN_EMAIL", self.atlassian_email),
                ("ATLASSIAN_API_TOKEN", self.atlassian_api_token),
                ("JIRA_BASE_URL", self.jira_base_url),
                ("JIRA_PROJECT_KEY", self.jira_project_key),
                ("CONFLUENCE_BASE_URL", self.confluence_base_url),
                ("CONFLUENCE_SPACE_KEY", self.confluence_space_key),
                ("CONFLUENCE_CONTEXT_PARENT_ID", self.confluence_context_parent_id),
                ("CONFLUENCE_ARTIFACTS_PARENT_ID", self.confluence_artifacts_parent_id),
            ]
            if not value
        ]
        if missing:
            raise ValueError(f"Missing Atlassian settings: {', '.join(missing)}")


def _normalize_base_url(value: str | None) -> str | None:
    if not value:
        return None
    return value.rstrip("/")
