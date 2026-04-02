# M1 | Main Control

## Purpose

`M1 | Main Control` is the control-tower thread for `AI_Japan_project`.

For the current cycle it owns:

- product-direction decisions
- demo-first prioritization
- React UX review and integration gates
- cleanup of stale Streamlit-era worktree noise

We are moving faster by executing this reset in one thread.

## Control Snapshot (2026-04-02)

- Stable baseline: `main@5dee3cc`
- Active branch for the current cycle: `main`
- Current demo surface: `react_ui/`
- Current product stance: `React-first`, `fixture-based`, `file-first manual handoff`
- Current design stance: `Light-first`, `Obsidian-led`, `Custom + Radix`
- Current demo target: `React workspace + personal agent + shared destination preview`
- Current handoff contract: stable request files in `project/runs/` and stable output files in `project/artifacts/`
- Streamlit status: frozen internal fallback
- Python harness status: still authoritative for future live integration boundaries

## Current Outcome

The near-term outcome is not "full platform completion".

The near-term outcome is:

`A React demo that makes the product understandable within one happy path`

Specifically:

- a user sees the current task
- the user sees which personal agent is connected
- the user understands the next action
- the user sees how the workflow reaches team share status

## Operating Rules

- React is the only active product UI surface in this cycle.
- Streamlit is not expanded further for product UX.
- The current demo uses a 3-step workspace:
  - `Task`
  - `Agent Handoff`
  - `Review & Share`
- Task picker and Context stay as support drawers, not full screens.
- The visual system follows the locked reference board:
  - Obsidian for document-led reading
  - ArgoCD for stage/state density
  - Atlassian for shared-with-team cues
- Task picker and Context are support panels, not separate full screens.
- The first connection model is `personal_agent`.
- The demo remains honest: handoff is manual, not automatic.
- The primary demo path is `file_handoff`.
- The demo does not require React-side result upload for this cycle.
- Internal implementation terms must not lead the UI.
  - avoid `packet`
  - avoid `artifact`
  - avoid `ingest`
  - avoid `frontmatter`
- Critic `approve` does not equal automatic completion.
- Final share/publish remains an operator decision.

## Product Boundaries

The React demo owns:

- information architecture
- product language
- handoff UX
- operator decision UX
- reference-driven visual iteration

The Python harness continues to own:

- orchestration logic
- state persistence
- Jira / Confluence sync
- parsing and state transitions in future live flows

## Active Deliverables

The current reset is complete only when all of the following exist together:

- React semantic action model
- explicit `copy_paste` / `file_handoff` handoff UI
- `ready_for_decision` instead of automatic `approved`
- refreshed product copy
- 3-step happy-path workspace
- frontend guidance locked in `AGENTS.md`
- design brief locked in `docs/react-demo-design-brief.md`
- reference board locked in `docs/react-demo-reference-board.md`
- React build passing
- updated screenshots
- `docs/react-demo-shot-list.md`
- updated `README.md`
- updated `docs/personal-agent-bridge-spec.md`

## Merge Gate

The React demo is merge-ready for this cycle only if:

1. the first fold shows `current task`, `connected agent`, `next action`, and one primary CTA
2. the workflow reads as `Task -> Agent Handoff -> Review & Share`
3. task picker and context are support panels, not full pages
4. no dead buttons remain
5. Critic output does not pretend to auto-complete the workflow
6. `cmd /c npm run build` passes

## Next Stage After This Cycle

Only after the React demo baseline is fixed do we open the next implementation seam:

- thin API adapter for React
- live task/context/result reads
- actual Jira / Confluence sync exposure in the React surface
