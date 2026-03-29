# AI_Japan_project

`AI_Japan_project` is a local-first demo app for a Japan-market AI agent PoC. It shows how a PM, operations lead, or other non-developer can run an AI workflow in the browser, moving from project context to requirements drafting and quality review.

The product flow is:

1. Edit project context
2. Create a PM task for a requirements draft
3. Generate a PM packet for an external agent such as Codex or Claude Code
4. Paste the PM result back into the app
5. Generate a Critic packet
6. Paste the Critic review back into the app
7. Track status, artifacts, and timeline in the UI

## Demo Scenario

- A Japanese retail company is evaluating whether business teams can operate AI-assisted workflows without waiting for a full internal tool build.
- The first workflow focuses on a PM agent drafting a requirements document and a Critic agent acting as a quality gate before stakeholder review.
- The demo is designed to highlight business clarity and operational control, not just model output.

## Stack

- Python 3.12
- Streamlit UI
- Shared Python service layer under `src/ai_japan_project`
- Local file storage under `project/`
- Optional Atlassian Cloud adapters for Jira and Confluence

## App Modes

The app supports two runtime modes.

- `AJP_MODE=local`
  - Default mode.
  - Canonical context, tasks, artifacts, and run history stay under `project/`.
  - No Atlassian credentials are required.
  - Tests should assume this mode never makes Jira or Confluence calls.
- `AJP_MODE=atlassian`
  - Jira Cloud becomes the canonical task store.
  - Confluence Cloud becomes the canonical context and artifact store.
  - Prompt packets and run history still stay local under `project/runs`.
  - Startup and tests should rely on config validation and injected seams, not on live Atlassian access.

## Atlassian Cloud Prerequisites

When `AJP_MODE=atlassian`, all of the following are required:

- `ATLASSIAN_EMAIL`: Atlassian account email paired with the API token for both Jira Cloud and Confluence Cloud.
- `ATLASSIAN_API_TOKEN`: API token created from the Atlassian account security settings page.
- `JIRA_BASE_URL`: Jira Cloud site root only, for example `https://example.atlassian.net`.
- `JIRA_PROJECT_KEY`: Jira project key where app tasks will be created and updated.
- `CONFLUENCE_BASE_URL`: Confluence Cloud site root including `/wiki`, for example `https://example.atlassian.net/wiki`.
- `CONFLUENCE_SPACE_KEY`: Confluence space key where the canonical project context and artifacts live.
- `CONFLUENCE_CONTEXT_PARENT_ID`: Existing numeric Confluence page ID under which `03_Context` will be created or updated.
- `CONFLUENCE_ARTIFACTS_PARENT_ID`: Existing numeric Confluence page ID under which generated artifact pages will be created or updated.

Validation that happens without live network calls:

- Missing Atlassian variables fail fast only when `AJP_MODE=atlassian`.
- Jira and Confluence base URLs are normalized and checked for the expected site shape.
- Confluence parent IDs are checked to be numeric page IDs.
- `factory.build_project_service(..., atlassian_client_factory=...)` can be exercised with a fake client factory.
- `AtlassianClient(..., opener=...)` can be exercised with a fake opener to verify auth headers, URLs, payloads, and HTTP error handling.

What is still not covered in this repo:

- Real Jira Cloud authentication with a live API token.
- Real Confluence Cloud page creation and permission checks.
- Site-specific Jira workflow transitions and Confluence space restrictions.

See `.env.example` for the full configuration template.

## Run

```powershell
cd D:\code\skax\AI_Japan_project
python -m streamlit run app_ui/streamlit_app.py
```

## Test

```powershell
cd D:\code\skax\AI_Japan_project
pytest tests -q
```

