import { useEffect, useState } from "react";

import { DashboardScreen } from "./screens/DashboardScreen";
import { ContextWorkspaceScreen } from "./screens/ContextWorkspaceScreen";
import { WorkflowWorkspaceScreen } from "./screens/WorkflowWorkspaceScreen";
import { ArtifactViewerScreen } from "./screens/ArtifactViewerScreen";
import { ShellLayout } from "../design-system/components/ShellLayout";
import { productData } from "../data/mockData";
import { ViewId } from "../types";

const VIEW_IDS: ViewId[] = ["dashboard", "context", "workflow", "artifacts"];

function readViewFromHash(): ViewId {
  if (typeof window === "undefined") {
    return "dashboard";
  }

  const hash = window.location.hash.replace("#", "");
  return VIEW_IDS.includes(hash as ViewId) ? (hash as ViewId) : "dashboard";
}

export default function App() {
  const [currentView, setCurrentView] = useState<ViewId>(readViewFromHash());

  useEffect(() => {
    const handleHashChange = () => setCurrentView(readViewFromHash());

    window.addEventListener("hashchange", handleHashChange);
    return () => window.removeEventListener("hashchange", handleHashChange);
  }, []);

  const navigate = (view: ViewId) => {
    window.location.hash = view;
    setCurrentView(view);
  };

  return (
    <ShellLayout
      connections={productData.connections}
      currentView={currentView}
      onNavigate={navigate}
      overview={productData.overview}
    >
      {currentView === "dashboard" ? <DashboardScreen data={productData} onNavigate={navigate} /> : null}
      {currentView === "context" ? <ContextWorkspaceScreen data={productData} onNavigate={navigate} /> : null}
      {currentView === "workflow" ? <WorkflowWorkspaceScreen data={productData} onNavigate={navigate} /> : null}
      {currentView === "artifacts" ? <ArtifactViewerScreen data={productData} onNavigate={navigate} /> : null}
    </ShellLayout>
  );
}
