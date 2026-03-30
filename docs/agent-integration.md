# External Agent Integration

## Core Idea

`AI_Japan_project` is not the agent itself. It is the orchestration surface around the agent.

The harness handles:

- context
- tasks
- packets
- artifacts
- Jira / Confluence synchronization

Your own agent handles:

- writing the PM draft
- writing the Critic review

That separation lets a team keep using Codex, Claude, or another internal assistant without rewriting the workflow layer.

## Supported Handoff Styles

### 1. Chat handoff

Use this when you want the fastest manual loop.

1. Generate the PM or Critic packet in the app
2. Copy the packet into a Codex or Claude chat
3. Tell the agent to return Markdown only
4. Paste the result back into the app

This is the simplest pattern for non-developers.

### 2. File handoff

Use this when your agent can read local files.

1. Generate the packet in the app
2. Give the external agent the packet file path under `project/runs/`
3. Let the agent read that file directly
4. Capture the Markdown response and paste it back into the app

This is useful for Codex / Claude Code style tools that can work from file paths.

### 3. Parallel handoff

Use this when you want PM and Critic to run in separate threads.

1. Generate the PM packet and send it to one agent thread
2. Ingest the PM result
3. Generate the Critic packet
4. Send that packet to a second thread or even a different agent product
5. Ingest the review back into the harness

This mirrors how role-based AI teams are often demonstrated in practice.

## Contract the External Agent Must Respect

### PM output

The PM agent should return a clean Markdown draft with the expected sections, for example:

- background
- goals
- functional requirements
- non-functional requirements
- open issues
- next actions

### Critic output

The Critic agent must return Markdown with YAML frontmatter. The current viewer parses this directly.

Example:

```markdown
---
verdict: revise
summary: The draft is clear but still misses measurable success criteria.
missing_items:
  - success metrics
recommended_changes:
  - add acceptance criteria for rollout readiness
---
The draft is structurally sound, but the business owner still cannot decide whether the PoC is ready for sign-off.
```

## Codex Example

A typical Codex prompt can be as small as:

> Read the attached packet and return only the requested Markdown output. Do not explain your process.

If you are using Codex with workspace access, the best experience is usually file handoff so the agent can read the packet directly.

## Claude Example

A typical Claude prompt can be:

> Use this packet as the full task contract. Return only the finished Markdown artifact, with no preamble.

For a browser chat, copy-paste handoff is usually enough.

## Why This Matters

This model keeps the harness stable even when the execution agent changes.

The user does not have to choose between:

- a workflow app with no real agent flexibility
- a powerful agent with no memory of project context or operational traceability

The harness provides the memory, traceability, and synchronization layer. Codex or Claude provides the reasoning step.
