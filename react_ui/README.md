# React UI Spike

This app is a standalone React product-surface spike for `AI_Japan_project`.

It does not replace the existing Streamlit shell. It exists to answer a narrower question:

- what should the future control-plane UI feel like?
- how should context, workflow, artifacts, and system connections sit together?
- what API boundary would let the Python harness back a richer frontend later?

## Stack

- Vite
- React
- TypeScript
- CSS token and component system defined locally under `src/design-system/`

## Run

```powershell
cd react_ui
cmd /c npm install
cmd /c npm run dev
```

## Build

```powershell
cd react_ui
cmd /c npm run build
```

## Notes

- The screens are fixture-driven on purpose.
- Current information architecture mirrors the existing `ProjectService` responsibilities.
- Transition guidance and proposed backend boundaries are documented in `../docs/react-ui-spike.md`.
