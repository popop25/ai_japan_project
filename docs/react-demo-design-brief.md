# React Demo Design Brief

## Goal

The current React demo should make this obvious within 10 seconds:

`My agent reads project context, continues the work, and the result becomes team share status.`

This is a demo brief, not a full product specification.

## Current Demo Story

The demo should stay narrow and linear.

Main flow:

1. `Task`
2. `Agent Handoff`
3. `Review & Share`

Support surfaces:

- `Task picker`
- `Context`

These should remain secondary.

## What The UI Must Communicate

The UI must make these four things obvious:

- what task we are looking at
- which agent is connected
- what the next action is
- how this becomes team share status

## What The UI Must Avoid

The UI should not feel like:

- a generic dashboard
- an internal admin tool
- a prompt engineering console
- a fake "AI does everything automatically" product

## Visual Direction

The intended direction is:

- calm document surface
- dense but quiet operational control
- one clear CTA per stage
- minimal decorative noise

Reference families:

- Notion: readable document feel
- ArgoCD: compact operational state
- Linear: decisive hierarchy and next action

These are directional references only, not literal cloning targets.

## Layout Constraints

- no persistent heavy left rail
- one primary story per screen
- one primary CTA above the fold
- task title and next action must be easy to spot
- team share state should become strongest in `Review & Share`

## Copy Constraints

Copy should be user-facing and action-centered.

Preferred language:

- `brief prepare`
- `send to agent`
- `confirm response ready`
- `request review`
- `apply review`
- `prepare team share`
- `check shared status`

Avoid leading with:

- `packet`
- `artifact`
- `ingest`
- `frontmatter`

## Design Tokens And Rhythm

Keep the visual system consistent:

- off-white surfaces
- deep navy primary action color
- muted informational states
- limited badge/chip variants
- consistent spacing scale
- consistent radius and shadow depth

Do not introduce random one-off color decisions.

## Responsive Expectations

Every meaningful UI change should be checked at:

- `390px`
- `768px`
- `1440px`

The primary CTA and main content should remain visible and legible.

## Required Reference Loop For Future UI Iterations

Before a major frontend polish pass, gather:

- current screenshot
- desired reference screenshot(s)
- mobile reference if available
- empty/loading/selected states if relevant
- Figma selection or layout reference if available

Without this, frontend polish should remain conservative.

## Demo Deliverables

Main screenshot set:

- `react_ui/screenshots/01-task.png`
- `react_ui/screenshots/02-agent-handoff.png`
- `react_ui/screenshots/03-review-share.png`

## Acceptance Checklist

The current demo direction is acceptable only if:

- the user understands the product in one pass
- the workflow reads as `Task -> Agent Handoff -> Review & Share`
- the CTA hierarchy is obvious
- the UI does not pretend handoff is automatic
- Jira and Confluence feel like team-sharing surfaces
