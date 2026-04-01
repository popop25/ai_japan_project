# AGENTS.md

This file defines the default frontend/product UI rules for `AI_Japan_project`.

These rules matter most when editing `react_ui/`.

## Product Frame

`AI_Japan_project` is not a built-in chatbot UI.

It is a platform where:

- project context is structured once
- a user connects their own agent
- the agent continues the work in role mode
- the result becomes team share status in Jira and Confluence

Frontend work must reinforce that message.

## Current Demo Scope

The active demo surface is `react_ui/`.

The current demo is intentionally narrow:

- fixture-based
- manual handoff
- one happy path
- three stages only

The main workflow is:

1. `Task`
2. `Agent Handoff`
3. `Review & Share`

Do not expand this into a broad multi-page workspace unless explicitly requested.

## Before Changing UI

Do not start a meaningful frontend redesign from copy alone.

Before substantial UI work, gather and use:

- at least one screenshot of the current page
- at least one visual reference for the desired direction
- ideally desktop and mobile references
- if available, hover/selected/empty/loading states
- if available, Figma selection URLs or equivalent design context

If those references are missing, say so and keep changes conservative.

## Design Constraints

When editing `react_ui/`, keep these constraints unless the user overrides them:

- one primary CTA above the fold
- no more than one main story per screen
- avoid persistent left rails unless explicitly needed
- no generic KPI dashboard layouts
- no repeated same-weight cards that flatten hierarchy
- section count should stay low and obvious
- typography roles must be clear
- `background`, `surface`, `primary text`, `muted text`, `accent` should stay tokenized
- do not add random hard-coded colors when existing tokens can do the job
- keep radius, shadow, spacing, and chip styles consistent

## UX Rules

UI copy must explain user value, not internal implementation.

Preferred concepts:

- current task
- connected agent
- next action
- team share status
- brief
- send
- receive
- review
- share

Avoid leading with internal terms such as:

- `packet`
- `artifact`
- `ingest`
- `frontmatter`
- raw backend enum names

Jira and Confluence should read as `shared with team`, not as raw proof panels.

Critic output must not read as automatic completion.

If the critic says approve, the UI should still show that operator decision is required.

## Responsive And State Requirements

Frontend work is not done until these are considered:

- `390px`
- `768px`
- `1440px`

And where relevant:

- hover
- focus
- selected
- empty
- loading
- disabled

Avoid floating or fixed UI that obscures the main CTA or content on smaller screens.

## Implementation Preferences

Inside `react_ui/`:

- prefer reusing the current `product-ux` structure
- prefer semantic action/state models over index-based UI logic
- prefer tokenized styling over ad hoc per-component colors
- keep component responsibilities small and explicit

Do not reintroduce removed legacy UI systems without a clear reason.

## Done Criteria For UI Work

A frontend change is not complete unless it includes:

- the implemented UI change
- a short explanation of visual/UX intent
- `cmd /c npm run build` passing
- screenshots for the relevant demo states
- any remaining risks or limitations

For the current demo baseline, the minimum screenshot set is:

- `01-task`
- `02-agent-handoff`
- `03-review-share`

## Current Taste Direction

Aim for:

- light-first
- calm document surface
- dense but quiet control panel
- clear hierarchy
- minimal but intentional emphasis

## Reference Freeze For The Current Cycle

The current React demo uses this reference mix:

- `Obsidian`
  - document surface
  - quiet chrome
  - readable note-like hierarchy
- `ArgoCD`
  - stage strip
  - dense status chips
  - operational clarity
- `Atlassian`
  - shared-with-team panel feel
  - enterprise workflow familiarity

Use them with this weight:

- Obsidian-led
- ArgoCD-supported
- Atlassian-accented

Do not copy those products literally.

For this cycle, explicitly avoid:

- heavy dark-mode mimicry from Obsidian
- engineering-console overload from ArgoCD
- complex global navigation from Atlassian
- gradient-heavy "AI product" hero blocks
