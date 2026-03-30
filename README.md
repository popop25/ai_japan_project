# AI_Japan_project

`AI_Japan_project` is a Streamlit-based AI work harness for business-facing workflows.

It is designed for a setup where the workflow platform and the reasoning agent are separate:

- the harness owns context, task state, packets, artifacts, and system-of-record sync
- the external agent owns the actual PM draft or Critic review generation

Today the project supports both a local demo mode and a live Atlassian-backed mode.

## What the Harness Owns

The project is organized around six responsibilities:

1. Context management
2. Task state management
3. PM / Critic packet generation
4. Artifact persistence
5. Jira / Confluence synchronization
6. External agent handoff orchestration

This is why the project should be thought of as a harness or control plane, not as a single embedded chatbot.

## Runtime Modes

### `AJP_MODE=local`

- Canonical context lives in `project/context.yaml` and `project/03_context.md`
- Tasks live in `project/tasks/*.yaml`
- Artifacts live in `project/artifacts/*.md`
- Prompt packets and run history live in `project/runs/*`
- No Atlassian credentials are required

### `AJP_MODE=atlassian`

- Jira is the canonical task store
- Confluence is the canonical context and artifact store
- Prompt packets and run history still remain local under `project/runs/*`
- The same Streamlit UI and `ProjectService` flow are reused

## Current Status

This repository is no longer just a local mockup.

The current codebase already includes:

- local / Atlassian mode switching
- Jira task synchronization with fail-closed issue existence checks
- Confluence context and artifact synchronization
- `.env` auto-loading with OS env precedence
- readiness / preflight tooling
- repeatable live smoke tooling
- smoke cleanup tooling
- live tenant hardening for localized Jira workflows and Confluence metadata fallback

A live end-to-end smoke run has already succeeded against a real Jira + Confluence tenant.

## Repository Map

- `app_ui/`
  - Streamlit UI shell and workflow screens
- `src/ai_japan_project/`
  - service layer, local stores, Atlassian adapters, operational tooling
- `project/`
  - seed context, skills, and local runtime data
- `scripts/`
  - readiness, smoke, and cleanup entry points
- `docs/`
  - architecture, operations, and external agent integration notes

## Run the App

```powershell
python -m streamlit run app_ui/streamlit_app.py
```

If you want to force Atlassian mode for the current shell:

```powershell
$env:AJP_MODE="atlassian"
python -m streamlit run app_ui/streamlit_app.py
```

## Operational Commands

### Readiness / preflight

```powershell
python scripts/ajp_readiness.py
python scripts/ajp_readiness.py --mode atlassian
```

### Live smoke run

```powershell
python scripts/ajp_smoke.py
```

### Smoke cleanup

```powershell
python scripts/ajp_cleanup.py
python scripts/ajp_cleanup.py --apply
```

### Tests

```powershell
pytest tests -q --basetemp=.tmp_test_runs\pytest
```

## Configuration

Keep your live Atlassian credentials in local environment variables or in a local `.env` file.

Settings are resolved in this order:

1. OS environment variables
2. repository `.env`

`.env` is ignored by Git. `.env.example` remains the checked-in template.

## External Agent Model

The project is intentionally agent-neutral.

The expected workflow is:

1. generate a PM or Critic packet in the app
2. send that packet to your own Codex, Claude, or equivalent agent
3. receive a Markdown result
4. paste the result back into the app
5. let the harness update local state plus Jira / Confluence as needed

Supported patterns include:

- chat handoff
- file handoff
- PM / Critic parallel handoff

See [agent integration](docs/agent-integration.md) for the practical patterns.

## Docs

- [Architecture](docs/architecture.md)
- [Operations](docs/operations.md)
- [External agent integration](docs/agent-integration.md)
