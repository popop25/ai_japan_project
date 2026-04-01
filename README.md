# AI_Japan_project

`AI_Japan_project` is a connected-agent workflow platform.

If project context is structured once, role-based AI agents can read it, continue the work, and hand the result back to the team through shared systems.

## Product Goal

The product we are trying to demonstrate is:

1. Confluence stores project context, decisions, and role instructions.
2. Jira stores the task lifecycle.
3. A user connects their own agent for PM and Critic work.
4. The workspace prepares the next handoff, receives the result, and keeps the flow moving.
5. The outcome is prepared for team sharing in Jira and Confluence.

This is not a built-in chatbot. It is workflow infrastructure for role-based agents.

## Current Demo Surface

The current cycle is React-first and reference-driven.

- `react_ui/`
  - current demo surface
  - fixture-based connected-agent workspace
  - 3-step happy path: `Task -> Agent Handoff -> Review & Share`
  - explicit manual handoff with `copy_paste` and `file_handoff`
  - visual direction: Obsidian-led document surface, ArgoCD-style state clarity, Atlassian-style team-sharing cues
- `app_ui/`
  - frozen internal fallback
  - not the active product direction for this cycle
- `src/ai_japan_project/`
  - Python harness and service layer
  - still owns orchestration, storage, and future live integration boundaries

## What The React Demo Proves

The React demo is intentionally honest about the current scope.

It proves:

- a user can understand the product within one happy path
- the workflow is centered on `task -> handoff -> review/share`
- PM and Critic are role-based agents, not hard-coded products
- Jira and Confluence are shown as shared-with-team surfaces

It does **not** yet prove:

- live API integration
- real-time agent connection
- automatic Jira / Confluence write-back from the React UI

Those are next-stage integration tasks after the demo UX baseline is fixed.

## Agent Model

The first supported connection model is `personal_agent`.

That means the user brings their own agent product such as Codex or Claude and uses it in role mode:

- `PM Agent`
- `Critic Agent`

The current demo supports these handoff patterns conceptually:

- `copy_paste`
- `file_handoff`

The app prepares the brief and the user performs the actual handoff manually.

## Repository Map

- `react_ui/`
  - React demo application
- `src/ai_japan_project/`
  - Python service layer, local stores, Atlassian adapters, operational tooling
- `project/`
  - seed context, skills, and local runtime data
- `scripts/`
  - readiness, smoke, and cleanup entry points
- `docs/`
  - architecture and product-direction notes

## Run The React Demo

```powershell
cd react_ui
cmd /c npm install
cmd /c npm run dev -- --host 127.0.0.1 --port 4173 --strictPort
```

Build check:

```powershell
cd react_ui
cmd /c npm run build
```

## Internal Fallback

The Streamlit app still exists for internal fallback and harness validation, but it is frozen for product UI work in this cycle.

```powershell
python -m streamlit run app_ui/streamlit_app.py
```

## Operational Commands

These still belong to the Python harness and remain useful for future live integration work:

```powershell
python scripts/ajp_readiness.py
python scripts/ajp_readiness.py --mode atlassian
python scripts/ajp_smoke.py
python scripts/ajp_cleanup.py
pytest tests -q --basetemp=.tmp_test_runs\pytest
```

## Docs

- [Architecture](docs/architecture.md)
- [Operations](docs/operations.md)
- [External agent integration](docs/agent-integration.md)
- [React demo design brief](docs/react-demo-design-brief.md)
- [React demo reference board](docs/react-demo-reference-board.md)
- [Personal agent bridge spec](docs/personal-agent-bridge-spec.md)
- [Main control notes](docs/main-control.md)
