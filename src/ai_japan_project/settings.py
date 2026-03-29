from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum
from urllib.parse import urlparse

from pydantic import BaseModel


class AppMode(str, Enum):
    LOCAL = "local"
    ATLASSIAN = "atlassian"


@dataclass(frozen=True)
class AtlassianEnvVar:
    name: str
    purpose: str
    example: str


ATLASSIAN_ENV_VARS: tuple[AtlassianEnvVar, ...] = (
    AtlassianEnvVar(
        name="ATLASSIAN_EMAIL",
        purpose="Atlassian account email paired with the API token for Jira Cloud and Confluence Cloud Basic auth.",
        example="demo@example.com",
    ),
    AtlassianEnvVar(
        name="ATLASSIAN_API_TOKEN",
        purpose="Atlassian API token generated from the Atlassian account security settings page.",
        example="atlassian_api_token_value",
    ),
    AtlassianEnvVar(
        name="JIRA_BASE_URL",
        purpose="Jira Cloud site root used for Jira REST API calls.",
        example="https://example.atlassian.net",
    ),
    AtlassianEnvVar(
        name="JIRA_PROJECT_KEY",
        purpose="Jira project key where AI Japan Project tasks will be created and updated.",
        example="AJP",
    ),
    AtlassianEnvVar(
        name="CONFLUENCE_BASE_URL",
        purpose="Confluence Cloud site root including /wiki, used for Confluence REST API calls and page links.",
        example="https://example.atlassian.net/wiki",
    ),
    AtlassianEnvVar(
        name="CONFLUENCE_SPACE_KEY",
        purpose="Confluence space key that stores the canonical project context and artifacts.",
        example="AJP",
    ),
    AtlassianEnvVar(
        name="CONFLUENCE_CONTEXT_PARENT_ID",
        purpose="Existing Confluence parent page ID under which the 03_Context page will be created or updated.",
        example="100",
    ),
    AtlassianEnvVar(
        name="CONFLUENCE_ARTIFACTS_PARENT_ID",
        purpose="Existing Confluence parent page ID under which generated artifact pages will be created or updated.",
        example="200",
    ),
)


class AtlassianSettings(BaseModel):
    atlassian_email: str
    atlassian_api_token: str
    jira_base_url: str
    jira_project_key: str
    confluence_base_url: str
    confluence_space_key: str
    confluence_context_parent_id: str
    confluence_artifacts_parent_id: str

    @classmethod
    def env_contract(cls) -> tuple[AtlassianEnvVar, ...]:
        return ATLASSIAN_ENV_VARS

    def validate_contract(self) -> None:
        errors: list[str] = []

        if "@" not in self.atlassian_email:
            errors.append("ATLASSIAN_EMAIL must look like an Atlassian account email address.")
        if any(character.isspace() for character in self.jira_project_key):
            errors.append("JIRA_PROJECT_KEY cannot contain whitespace.")

        jira_url_error = _validate_https_url(
            "JIRA_BASE_URL",
            self.jira_base_url,
            expected_path="",
            example="https://example.atlassian.net",
        )
        if jira_url_error:
            errors.append(jira_url_error)

        confluence_url_error = _validate_https_url(
            "CONFLUENCE_BASE_URL",
            self.confluence_base_url,
            expected_path="/wiki",
            example="https://example.atlassian.net/wiki",
        )
        if confluence_url_error:
            errors.append(confluence_url_error)

        for name, value in [
            ("CONFLUENCE_CONTEXT_PARENT_ID", self.confluence_context_parent_id),
            ("CONFLUENCE_ARTIFACTS_PARENT_ID", self.confluence_artifacts_parent_id),
        ]:
            if not value.isdigit():
                errors.append(f"{name} must be a numeric Confluence page ID.")

        if errors:
            formatted_errors = "\n- ".join(errors)
            raise ValueError(f"Invalid Atlassian settings:\n- {formatted_errors}")


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
        raw_mode = _read_env("AJP_MODE") or AppMode.LOCAL.value
        return cls(
            mode=AppMode(raw_mode),
            atlassian_email=_read_env("ATLASSIAN_EMAIL"),
            atlassian_api_token=_read_env("ATLASSIAN_API_TOKEN"),
            jira_base_url=_normalize_base_url(_read_env("JIRA_BASE_URL")),
            jira_project_key=_read_env("JIRA_PROJECT_KEY"),
            confluence_base_url=_normalize_base_url(_read_env("CONFLUENCE_BASE_URL")),
            confluence_space_key=_read_env("CONFLUENCE_SPACE_KEY"),
            confluence_context_parent_id=_read_env("CONFLUENCE_CONTEXT_PARENT_ID"),
            confluence_artifacts_parent_id=_read_env("CONFLUENCE_ARTIFACTS_PARENT_ID"),
        )

    def missing_atlassian_settings(self) -> list[str]:
        return [
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

    def atlassian_settings(self) -> AtlassianSettings:
        missing = self.missing_atlassian_settings()
        if missing:
            raise ValueError(
                "Missing Atlassian settings for AJP_MODE=atlassian: "
                + ", ".join(missing)
            )

        settings = AtlassianSettings(
            atlassian_email=self.atlassian_email or "",
            atlassian_api_token=self.atlassian_api_token or "",
            jira_base_url=self.jira_base_url or "",
            jira_project_key=self.jira_project_key or "",
            confluence_base_url=self.confluence_base_url or "",
            confluence_space_key=self.confluence_space_key or "",
            confluence_context_parent_id=self.confluence_context_parent_id or "",
            confluence_artifacts_parent_id=self.confluence_artifacts_parent_id or "",
        )
        settings.validate_contract()
        return settings

    def validate_atlassian(self) -> None:
        self.atlassian_settings()


def _read_env(name: str) -> str | None:
    value = os.getenv(name)
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _normalize_base_url(value: str | None) -> str | None:
    if not value:
        return None
    return value.rstrip("/")


def _validate_https_url(
    name: str,
    value: str,
    *,
    expected_path: str,
    example: str,
) -> str | None:
    parsed = urlparse(value)
    normalized_path = parsed.path.rstrip("/")
    if parsed.scheme != "https" or not parsed.netloc:
        return f"{name} must be a full https URL. Example: {example}"
    if normalized_path != expected_path:
        return f"{name} must match {example}"
    if parsed.params or parsed.query or parsed.fragment:
        return f"{name} cannot include params, query strings, or fragments."
    return None
