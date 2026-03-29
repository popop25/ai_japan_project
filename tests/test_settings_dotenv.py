from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from ai_japan_project.settings import AppMode, AppSettings


DOTENV_KEYS = (
    "AJP_MODE",
    "ATLASSIAN_EMAIL",
    "ATLASSIAN_API_TOKEN",
    "JIRA_BASE_URL",
    "JIRA_PROJECT_KEY",
    "CONFLUENCE_BASE_URL",
    "CONFLUENCE_SPACE_KEY",
    "CONFLUENCE_CONTEXT_PARENT_ID",
    "CONFLUENCE_ARTIFACTS_PARENT_ID",
)


def _clear_env(monkeypatch) -> None:
    for key in DOTENV_KEYS:
        monkeypatch.delenv(key, raising=False)


def _make_dotenv_path() -> Path:
    base_dir = Path(".tmp_test_runs") / f"dotenv_{uuid.uuid4().hex}"
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir / ".env"


def test_app_settings_reads_repo_style_dotenv_file(monkeypatch) -> None:
    _clear_env(monkeypatch)
    dotenv_path = _make_dotenv_path()
    try:
        dotenv_path.write_text(
            "\n".join(
                [
                    "AJP_MODE=atlassian",
                    "ATLASSIAN_EMAIL=dotenv@example.com",
                    "ATLASSIAN_API_TOKEN='dotenv-token'",
                    "JIRA_BASE_URL=https://example.atlassian.net/",
                    "JIRA_PROJECT_KEY=AJP",
                    "CONFLUENCE_BASE_URL=https://example.atlassian.net/wiki/",
                    "CONFLUENCE_SPACE_KEY=DEMO",
                    "CONFLUENCE_CONTEXT_PARENT_ID=100",
                    "CONFLUENCE_ARTIFACTS_PARENT_ID=200",
                ]
            ),
            encoding="utf-8",
        )

        settings = AppSettings.from_env(dotenv_path=dotenv_path)
        resolved = settings.atlassian_settings()

        assert settings.mode == AppMode.ATLASSIAN
        assert resolved.atlassian_email == "dotenv@example.com"
        assert resolved.atlassian_api_token == "dotenv-token"
        assert resolved.jira_base_url == "https://example.atlassian.net"
        assert resolved.confluence_base_url == "https://example.atlassian.net/wiki"
    finally:
        shutil.rmtree(dotenv_path.parent, ignore_errors=True)


def test_os_environment_overrides_dotenv_values(monkeypatch) -> None:
    _clear_env(monkeypatch)
    dotenv_path = _make_dotenv_path()
    try:
        dotenv_path.write_text(
            "\n".join(
                [
                    "AJP_MODE=atlassian",
                    "ATLASSIAN_EMAIL=dotenv@example.com",
                    "ATLASSIAN_API_TOKEN=dotenv-token",
                    "JIRA_BASE_URL=https://dotenv.atlassian.net",
                    "JIRA_PROJECT_KEY=DOT",
                    "CONFLUENCE_BASE_URL=https://dotenv.atlassian.net/wiki",
                    "CONFLUENCE_SPACE_KEY=DOT",
                    "CONFLUENCE_CONTEXT_PARENT_ID=100",
                    "CONFLUENCE_ARTIFACTS_PARENT_ID=200",
                ]
            ),
            encoding="utf-8",
        )
        monkeypatch.setenv("ATLASSIAN_EMAIL", "os@example.com")
        monkeypatch.setenv("JIRA_PROJECT_KEY", "KAN")

        settings = AppSettings.from_env(dotenv_path=dotenv_path)
        resolved = settings.atlassian_settings()

        assert resolved.atlassian_email == "os@example.com"
        assert resolved.jira_project_key == "KAN"
        assert resolved.atlassian_api_token == "dotenv-token"
    finally:
        shutil.rmtree(dotenv_path.parent, ignore_errors=True)


def test_missing_dotenv_file_keeps_local_defaults(monkeypatch) -> None:
    _clear_env(monkeypatch)
    missing_path = Path(".tmp_test_runs") / f"missing_{uuid.uuid4().hex}" / ".env"

    settings = AppSettings.from_env(dotenv_path=missing_path)

    assert settings.mode == AppMode.LOCAL
    assert settings.missing_atlassian_settings() == [
        "ATLASSIAN_EMAIL",
        "ATLASSIAN_API_TOKEN",
        "JIRA_BASE_URL",
        "JIRA_PROJECT_KEY",
        "CONFLUENCE_BASE_URL",
        "CONFLUENCE_SPACE_KEY",
        "CONFLUENCE_CONTEXT_PARENT_ID",
        "CONFLUENCE_ARTIFACTS_PARENT_ID",
    ]
