from __future__ import annotations

from .atlassian import (
    AtlassianArtifactStore,
    AtlassianClient,
    AtlassianContextStore,
    AtlassianTaskStore,
)
from .handoff import LocalPromptHandoffService
from .service import ProjectService
from .settings import AppMode, AppSettings
from .storage import LocalArtifactStore, LocalContextStore, LocalRunStore, LocalTaskStore


def build_project_service(settings: AppSettings | None = None) -> ProjectService:
    settings = settings or AppSettings.from_env()
    prompt_service = LocalPromptHandoffService()
    run_store = LocalRunStore()

    if settings.mode == AppMode.LOCAL:
        return ProjectService(
            context_store=LocalContextStore(),
            task_store=LocalTaskStore(),
            artifact_store=LocalArtifactStore(),
            run_store=run_store,
            prompt_service=prompt_service,
        )

    settings.validate_atlassian()
    client = AtlassianClient(
        email=settings.atlassian_email or "",
        api_token=settings.atlassian_api_token or "",
        jira_base_url=settings.jira_base_url or "",
        confluence_base_url=settings.confluence_base_url or "",
    )
    return ProjectService(
        context_store=AtlassianContextStore(
            client,
            space_key=settings.confluence_space_key or "",
            parent_page_id=settings.confluence_context_parent_id or "",
            bootstrap_store=LocalContextStore(),
        ),
        task_store=AtlassianTaskStore(client, project_key=settings.jira_project_key or ""),
        artifact_store=AtlassianArtifactStore(
            client,
            space_key=settings.confluence_space_key or "",
            parent_page_id=settings.confluence_artifacts_parent_id or "",
        ),
        run_store=run_store,
        prompt_service=prompt_service,
    )
