# External Agent Integration

## Core Idea

`AI_Japan_project` is not the agent itself. It is the workspace around the agent.

The React demo does three things:

- shows the current task and the next handoff
- shows which agent role should take the next step
- shows where the team-facing result is expected to land

The personal agent does the actual work:

- reads the request file
- writes the output file
- returns control to the operator for the next stage

## Default Demo Contract

The default demo path is `file_handoff`.

Before the demo starts, prepare the stable runtime files:

```powershell
python scripts/prepare_react_demo_handoff.py
```

This creates:

- `project/runs/demo_requirements_draft_request.md`
- `project/runs/demo_requirements_review_request.md`
- `project/artifacts/demo_requirements_draft.md`
- `project/artifacts/demo_requirements_review.md`

These are the stable files the React demo and the personal agent both point to.

## PM Agent Flow

1. Open `Task` in React.
2. Move to `에이전트 전달`.
3. Confirm the PM request file path:
   - `project/runs/demo_requirements_draft_request.md`
4. Let the PM agent read that file directly.
5. The PM agent writes the result to:
   - `project/artifacts/demo_requirements_draft.md`
6. Return to React and use `작업 완료 확인` to continue.

## Critic Agent Flow

1. Move to the Critic handoff step in React.
2. Confirm the Critic request file path:
   - `project/runs/demo_requirements_review_request.md`
3. Let the Critic agent read that file directly.
4. The Critic agent writes the result to:
   - `project/artifacts/demo_requirements_review.md`
5. Return to React and use `작업 완료 확인` to continue.

## What React Does Not Do In This Demo

The current demo does **not**:

- upload results back into React
- parse output files live
- perform actual Jira / Confluence write-back
- own the full workflow persistence loop

React stays honest as a `workspace / handoff / confirmation` surface.

## Optional Pre-Demo Publish Step

If we want one Jira issue and the related Confluence pages ready before recording, use the Python harness separately:

```powershell
python scripts/publish_react_demo_outputs.py --cleanup-existing
```

This does not change the React contract. It simply takes the current output files, creates the external team-facing resources, and prints the Jira / Confluence links that can be used as the final proof shot.

## Optional Fallback

`copy_paste` still exists as a fallback mode.

Use it only when the external agent cannot read local files directly.
The primary demo path remains `file_handoff`.

## Codex Example

For a Codex thread with workspace access, a minimal ask is:

> Read `project/runs/demo_requirements_draft_request.md`, follow the contract, and write the result to `project/artifacts/demo_requirements_draft.md`.

For Critic:

> Read `project/runs/demo_requirements_review_request.md`, follow the contract, and write the result to `project/artifacts/demo_requirements_review.md`.

## Why This Matters

This keeps the product story consistent:

- React prepares the handoff
- the user's own agent does the work
- React confirms the next stage and the final team-share destination

That is the behavior we want the demo to prove.
