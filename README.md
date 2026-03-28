# AI_Japan_project

`AI_Japan_project` is a local-first demo app for showing that a non-developer can use an AI work platform in the browser.

The demo flow is:

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

## Run

```powershell
cd D:\code\skax\AI_Japan_project
streamlit run app_ui\streamlit_app.py
```

## Test

```powershell
cd D:\code\skax\AI_Japan_project
pytest tests -q
```

