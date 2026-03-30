# React UI Spike

## Purpose

This spike proposes the next UI direction for `AI_Japan_project` without replacing the current Streamlit shell.

The goal is to make the product feel like an AI workflow control plane:

- context is visible and editable
- workflow state is explicit
- PM and Critic handoff stays operator-led
- artifacts are readable before raw markdown
- Jira and Confluence feel like connected systems, not bolt-ons

## Stack

- Vite
- React
- TypeScript
- local CSS tokens and shared UI primitives
- fixture-driven data aligned to the current harness model

## File Structure

```text
react_ui/
  src/
    app/
      App.tsx
      screens/
        DashboardScreen.tsx
        ContextWorkspaceScreen.tsx
        WorkflowWorkspaceScreen.tsx
        ArtifactViewerScreen.tsx
    data/mockData.ts
    design-system/
      tokens.css
      base.css
      components/
        ShellLayout.tsx
        Panel.tsx
        Card.tsx
        StatusBadge.tsx
        Chip.tsx
        DocView.tsx
        Stepper.tsx
    types.ts
    utils.ts
```

## Design System Direction

The design system is intentionally product-first rather than dashboard-first.

### Visual rules

- Warm neutral canvas with blue and teal accents for trust rather than flashy demo aesthetics
- Distinct surface layers for shell, panels, cards, and documents
- Strong display typography for hierarchy, with calmer body typography for longer reading
- Status colors reserved for workflow meaning: progress, review-ready, revision-needed, connected
- Rounded but structured containers to feel modern without becoming soft or consumer-like

### Shared primitives

- `ShellLayout`: persistent control-plane frame with global state, navigation, next action, and connection status
- `Panel`: primary content container for screen-level sections
- `Card`: compact summary unit for metrics, artifacts, and connection summaries
- `StatusBadge`: workflow and system status mapping in one component
- `Chip`: secondary labeling for mode, posture, and metadata
- `DocView`: reusable narrative + outline reader for context and artifacts
- `Stepper`: guided workflow track that keeps operator action and outcome visible together

## Reference Translation

### Linear

Applied ideas:

- fast information hierarchy on the dashboard
- next action shown ahead of secondary metadata
- queue, progress, and artifact signals grouped into one operating read
- project graph-style progress signal to show movement and scope together

### Atlassian Teamwork Collection / Rovo

Applied ideas:

- knowledge, execution, and tracking shown in one shell
- Jira and Confluence treated as connected system surfaces, not hidden integrations
- external AI agents represented as teammates in the workflow, not embedded magic

### Notion Docs / Projects

Applied ideas:

- document readability in the context workspace
- structured fields and narrative brief side by side
- artifact viewer optimized for summary-first reading before raw source

### OpenAI quality bar

Applied ideas:

- real content and specific workflow copy instead of placeholder widgets
- product shell built around believable operator tasks
- visual polish focused on clarity, not a generic analytics dashboard pattern

## Implemented Screens

### Dashboard

- current situation
- next operator action
- work queue
- project graph signal
- connected systems
- recent activity
- latest artifacts

### Context Workspace

- narrative context document
- structured state fields
- decisions log
- operator posture guidance

### Workflow Workspace

- current workflow state
- guided stepper
- packet preview
- handoff mode options
- run trace
- operator checklist
- downstream sync preview

### Artifact Viewer

- summary-first artifact switching
- traceability links to Jira and Confluence
- operator readout
- reusable document viewer for PM draft, Critic review, and context snapshot

## Proposed Backend Boundary

The safest React transition is to preserve the existing `ProjectService` responsibilities and expose view models over API endpoints.

Suggested minimum boundary:

- `GET /api/overview`
- `GET /api/context`
- `PATCH /api/context`
- `GET /api/tasks/:taskId/workflow`
- `POST /api/tasks/:taskId/workflow/actions`
- `GET /api/artifacts/:artifactId`

Rules behind that boundary:

- keep task transitions in Python service code
- keep packet generation in Python service code
- keep Critic markdown/frontmatter parsing in backend contracts unless frontend parsing is intentionally adopted
- keep Atlassian mode differences hidden behind the API instead of branching in React

## Current Limitations

- fixture-driven only; no live Python or Atlassian integration yet
- no edit persistence from the React app
- no authenticated API layer yet
- no routing library; the spike uses a lightweight hash-based view switch because the goal is shell and IA validation first

## Recommended Next Steps

1. Add a thin API layer that serializes `DashboardData`, `TaskDetail`, context, and artifact view models.
2. Decide whether artifact and review parsing stays server-side or becomes a shared schema.
3. Introduce real context/task fetches first, while keeping packet dispatch and ingest server-driven.
4. Validate the React shell with one live workflow end to end before considering Streamlit replacement.
