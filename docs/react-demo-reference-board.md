# React Demo Reference Board

## Goal

This reference board freezes the visual direction for the current React demo pass.

The target is a light, calm, product-facing workspace that makes one happy path obvious:

`Task -> Agent Handoff -> Review & Share`

## Reference Mix

### Obsidian

Keep:

- document-led reading surface
- quiet top chrome
- generous line-height and readable text hierarchy
- note-like panels that feel intentional rather than dashboard-like

Avoid:

- full dark-mode recreation
- plugin-like clutter
- multi-column note explorer UI

### ArgoCD

Keep:

- explicit stage strip
- compact state chips
- clear health / waiting / action-needed signaling
- dense but legible status blocks

Avoid:

- infrastructure-console overload
- multi-filter admin control bars
- repeated action buttons on every card

### Atlassian

Keep:

- familiar work-tool clarity
- shared-with-team cues for Jira / Confluence
- enterprise-product confidence without excessive decoration

Avoid:

- full global navigation mimicry
- crowded utility bars
- "everything is a card" layout

## Visual Translation

### Layout

- no persistent left rail
- no generic dashboard grid
- one main story per screen
- one primary CTA above the fold
- task picker and context are support drawers, not full pages

### Surface Model

- `background`: one light canvas
- `surface`: quiet document panel
- `surface-muted`: restrained support panel
- `accent`: deep navy only for important emphasis
- `status`: three tones only
  - healthy
  - attention
  - waiting

### Type Roles

- `display`
- `title`
- `section`
- `body`
- `caption`

The UI should feel more like a focused work product than an AI landing page.

## Component Guidance

### Task

- document-led hero
- task title, next action, connected agent, primary CTA
- shared-with-team shown as a small summary only

### Agent Handoff

- segmented mode selector for `copy_paste` and `file_handoff`
- document card for the brief
- compact operational side block for status and expected response

### Review & Share

- review summary and operator decision on the left
- Jira / Confluence shared-with-team panel on the right
- review verdict must not look like automatic completion

## Anti-Patterns

Do not introduce:

- oversized hero explanations
- four same-weight summary cards
- random gradients or glowing AI visuals
- technical backend language in the main UX
- dead buttons or index-based action mapping

## Done Signal

The redesign is successful when:

1. the first fold explains the product in about ten seconds
2. the layout feels calmer and less AI-generated
3. state is easier to scan without looking like an ops console
4. Jira / Confluence read as team-sharing surfaces, not proof widgets
