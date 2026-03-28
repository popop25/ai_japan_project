# AI_Japan_project

`AI_Japan_project` is a local-first demo app that shows how a non-developer can run an AI work platform in the browser.

The product flow is:

1. Edit project context
2. Create a PM task for a requirements draft
3. Generate a PM packet for an external agent such as Codex or Claude Code
4. Paste the PM result back into the app
5. Generate a Critic packet
6. Paste the Critic review back into the app
7. Track status, artifacts, and timeline in the UI

## Stack

- Python 3.12
- Streamlit UI
- Shared Python service layer under `src/ai_japan_project`
- Local file storage under `project/`
- Optional Atlassian Cloud adapters for Jira and Confluence

## App Modes

The app supports two runtime modes.

- `AJP_MODE=local`: file-based demo mode using `project/context.yaml`, `project/tasks`, `project/artifacts`, and `project/runs`
- `AJP_MODE=atlassian`: Jira Cloud + Confluence Cloud mode using API tokens for canonical task/context/artifact storage

When `AJP_MODE=atlassian`, set these environment variables:

- `ATLASSIAN_EMAIL`
- `ATLASSIAN_API_TOKEN`
- `JIRA_BASE_URL`
- `JIRA_PROJECT_KEY`
- `CONFLUENCE_BASE_URL`
- `CONFLUENCE_SPACE_KEY`
- `CONFLUENCE_CONTEXT_PARENT_ID`
- `CONFLUENCE_ARTIFACTS_PARENT_ID`

See `.env.example` for the full list.

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
