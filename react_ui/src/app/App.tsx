import { useEffect, useState } from "react";

import { DashboardScreen } from "./screens/DashboardScreen";
import { ContextWorkspaceScreen } from "./screens/ContextWorkspaceScreen";
import { WorkflowWorkspaceScreen } from "./screens/WorkflowWorkspaceScreen";
import { ArtifactViewerScreen } from "./screens/ArtifactViewerScreen";
import { AppShell } from "../design-system/components/AppShell";
import { productData } from "../data/mockData";
import { PrototypeScreenState, ViewId } from "../types";

const VIEW_IDS: ViewId[] = ["dashboard", "context", "workflow", "artifacts"];
const SCREEN_STATE_KEYS = ["dashboard", "workflow", "artifacts"] as const;

type ScreenStateKey = (typeof SCREEN_STATE_KEYS)[number];
type ScreenStateMap = Record<ScreenStateKey, PrototypeScreenState>;

const DEFAULT_SCREEN_STATES: ScreenStateMap = {
  dashboard: "ready",
  workflow: "ready",
  artifacts: "ready",
};

function isPrototypeScreenState(value: string | null): value is PrototypeScreenState {
  return value === "ready" || value === "loading" || value === "error" || value === "empty";
}

function readViewFromHash(fallback: ViewId = "dashboard"): ViewId {
  if (typeof window === "undefined") {
    return fallback;
  }

  const hash = window.location.hash.replace("#", "");
  return VIEW_IDS.includes(hash as ViewId) ? (hash as ViewId) : fallback;
}

function readScreenStatesFromSearch(): ScreenStateMap {
  if (typeof window === "undefined") {
    return { ...DEFAULT_SCREEN_STATES };
  }

  const params = new URLSearchParams(window.location.search);
  const nextState = { ...DEFAULT_SCREEN_STATES };

  SCREEN_STATE_KEYS.forEach((key) => {
    const value = params.get(`${key}State`) ?? params.get(key);

    if (isPrototypeScreenState(value)) {
      nextState[key] = value;
    }
  });

  return nextState;
}

function clearPrototypeStateSearchParams() {
  if (typeof window === "undefined") {
    return;
  }

  const url = new URL(window.location.href);

  SCREEN_STATE_KEYS.forEach((key) => {
    url.searchParams.delete(key);
    url.searchParams.delete(`${key}State`);
  });

  window.history.replaceState(null, "", `${url.pathname}${url.search}${url.hash}`);
}

export default function App() {
  const [currentView, setCurrentView] = useState<ViewId>(() => readViewFromHash("dashboard"));
  const [screenStates, setScreenStates] = useState<ScreenStateMap>(readScreenStatesFromSearch);

  useEffect(() => {
    const handleHashChange = () => setCurrentView((previousView) => readViewFromHash(previousView));

    window.addEventListener("hashchange", handleHashChange);
    return () => window.removeEventListener("hashchange", handleHashChange);
  }, []);

  const navigate = (view: ViewId) => {
    window.location.hash = view;
    setCurrentView(view);
  };

  const resetPrototypeStates = () => {
    setScreenStates({ ...DEFAULT_SCREEN_STATES });
    clearPrototypeStateSearchParams();
  };

  return (
    <AppShell
      connections={productData.connections}
      currentView={currentView}
      onNavigate={navigate}
      overview={productData.overview}
      queue={productData.queue}
      workflow={productData.workflow}
    >
      {currentView === "dashboard" ? (
        <DashboardScreen data={productData} onNavigate={navigate} onResetState={resetPrototypeStates} state={screenStates.dashboard} />
      ) : null}
      {currentView === "context" ? <ContextWorkspaceScreen data={productData} onNavigate={navigate} /> : null}
      {currentView === "workflow" ? (
        <WorkflowWorkspaceScreen
          data={productData}
          onNavigate={navigate}
          onResetState={resetPrototypeStates}
          state={screenStates.workflow}
        />
      ) : null}
      {currentView === "artifacts" ? (
        <ArtifactViewerScreen
          data={productData}
          onNavigate={navigate}
          onResetState={resetPrototypeStates}
          state={screenStates.artifacts}
        />
      ) : null}
    </AppShell>
  );
}
