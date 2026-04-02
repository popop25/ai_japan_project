# Personal Agent Bridge Spec

## Goal

The first supported connection model for `AI_Japan_project` is `personal_agent`.

This means the user brings their own agent product and uses it in role mode inside the workflow:

- `PM Agent`
- `Critic Agent`

The product is not tied to one vendor. Codex and Claude are examples, not the contract.

## Core Product Promise

If project context is already structured, the workspace should help the user:

1. open the current task
2. prepare the right brief for the current role
3. send that brief to their own agent
4. confirm that the agent work is ready for the next stage
5. move to review and team sharing

The current demo expresses this promise through a 3-step workspace:

- `Task`
- `Agent Handoff`
- `Review & Share`

## Roles

### PM Agent

- reads the task and context
- produces the initial draft
- works from a brief prepared by the workspace

### Critic Agent

- reviews the PM draft
- returns a verdict and summary
- identifies missing items or reasons to revise

### Operator

- chooses the task
- decides how to hand off to the agent
- confirms the next stage in the workspace after agent work
- makes the final share decision

## Supported Connection Modes

### `copy_paste`

- the app prepares the brief
- the user copies it into their agent chat
- the user returns to the workspace and confirms the next stage after the agent work

### `file_handoff`

- the app prepares a stable request file path and a stable output file path
- the user hands the request file path to their agent
- the agent reads the request file directly and writes the result to the output path
- the user returns to the workspace and confirms the next stage after the agent work

The current React demo shows both modes explicitly, but the primary demo path is `file_handoff`.

## User-Visible Workflow States

The UI should use business-readable states, not backend enums.

- `not_started`
- `brief_ready`
- `waiting_for_agent`
- `response_received`
- `review_requested`
- `ready_for_decision`
- `revise`
- `shared`

Important rule:

- Critic `approve` does **not** skip the operator.
- Critic `approve` maps to `ready_for_decision`.
- Final share or publish is still an operator action.

## Product Language

Use these front-stage labels:

- `brief ready`
- `send to agent`
- `confirm work complete`
- `request review`
- `apply review`
- `prepare team share`
- `check share status`

Avoid these front-stage labels:

- `packet`
- `artifact`
- `ingest`
- `frontmatter`
- `run session`

Those remain implementation details.

## Responsibility Split

### Frontend

- show the current task
- show the connected agent
- show the next action
- show how the result will be shared with the team
- guide the user through manual handoff

### Backend / Harness

- keep the authoritative workflow model
- generate briefs
- persist results
- handle Jira and Confluence synchronization
- parse structured review payloads in future live integration work

## Happy Path

1. The user opens a task.
2. The workspace shows the current task, the connected PM agent, and the next action.
3. The user opens `Agent Handoff`.
4. The workspace shows the brief, the selected handoff mode, the request file path, and the output file path.
5. The user sends the request file to their PM agent.
6. The user completes the PM work in their own agent and returns to the workspace.
7. The workspace moves to Critic review.
8. The user sends the Critic request file to their Critic agent.
9. The user completes the Critic review in their own agent and returns to the workspace.
10. The workspace shows `ready_for_decision` or `revise`.
11. The operator decides whether to share or revise.
12. The resulting state is prepared for Jira and Confluence team sharing.

## Shared-With-Team Model

Jira and Confluence should appear as team-sharing surfaces, not raw proof panels.

The UI should show:

- current share status
- short human-readable summary
- last update timing

The UI should avoid showing raw storage paths or machine metadata as the main story.

## Naming Guidance

### Task title

- short, human-readable, outcome-oriented
- example: `점포 운영 AI 적용 범위 정리`

### Draft title

- readable as a team document
- example: `요구사항 정의서 초안`

### Review title

- readable as a team review state
- example: `요구사항 초안 검토 의견`

## Next Technical Seam

This spec is written for the current React fixture demo.

The next implementation seam after the demo baseline is stable is:

- a thin API adapter
- task, context, and result reads
- explicit action endpoints for brief preparation and result application
