from __future__ import annotations

from collections.abc import Callable

from .atlassian import (
    AtlassianArtifactStore,
    AtlassianClient,
    AtlassianContextStore,
    AtlassianServiceClient,
    AtlassianTaskStore,
)
from .handoff import LocalPromptHandoffService
from .service import ProjectService
from .settings import AppMode, AppSettings, AtlassianSettings
from .storage import LocalArtifactStore, LocalContextStore, LocalRunStore, LocalTaskStore

AtlassianClientFactory = Callable[[AtlassianSettings], AtlassianServiceClient]


def build_project_service(
    settings: AppSettings | None = None,
    *,
    atlassian_client_factory: AtlassianClientFactory | None = None,
) -> ProjectService:
    settings = settings or AppSettings.from_env()
    prompt_service = LocalPromptHandoffService()
    # Prompt packets and run history remain local in both modes.
    run_store = LocalRunStore()

    if settings.mode == AppMode.LOCAL:
        return _build_local_project_service(prompt_service=prompt_service, run_store=run_store)

    atlassian_settings = settings.atlassian_settings()
    client_factory = atlassian_client_factory or AtlassianClient.from_settings
    client = client_factory(atlassian_settings)
    return _build_atlassian_project_service(
        client=client,
        atlassian_settings=atlassian_settings,
        prompt_service=prompt_service,
        run_store=run_store,
    )


def _build_local_project_service(
    *,
    prompt_service: LocalPromptHandoffService,
    run_store: LocalRunStore,
) -> ProjectService:
    return ProjectService(
        context_store=LocalContextStore(),
        task_store=LocalTaskStore(),
        artifact_store=LocalArtifactStore(),
        run_store=run_store,
        prompt_service=prompt_service,
    )


def _build_atlassian_project_service(
    *,
    client: AtlassianServiceClient,
    atlassian_settings: AtlassianSettings,
    prompt_service: LocalPromptHandoffService,
    run_store: LocalRunStore,
) -> ProjectService:
    return ProjectService(
        context_store=AtlassianContextStore(
            client,
            space_key=atlassian_settings.confluence_space_key,
            parent_page_id=atlassian_settings.confluence_context_parent_id,
            bootstrap_store=LocalContextStore(),
        ),
        task_store=AtlassianTaskStore(client, project_key=atlassian_settings.jira_project_key),
        artifact_store=AtlassianArtifactStore(
            client,
            space_key=atlassian_settings.confluence_space_key,
            parent_page_id=atlassian_settings.confluence_artifacts_parent_id,
        ),
        run_store=run_store,
        prompt_service=prompt_service,
    )
