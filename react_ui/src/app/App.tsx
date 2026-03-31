import { useState } from "react";

import { AppShell } from "./product-ux/components/AppShell";
import { AgentHandoffScreen } from "./product-ux/screens/AgentHandoffScreen";
import { ContextViewScreen } from "./product-ux/screens/ContextViewScreen";
import { ReviewResultScreen } from "./product-ux/screens/ReviewResultScreen";
import { TaskDetailScreen } from "./product-ux/screens/TaskDetailScreen";
import { TaskInboxWorkboardScreen } from "./product-ux/screens/TaskInboxWorkboardScreen";
import { productExperience } from "./product-ux/productData";
import { ProductViewId } from "./product-ux/types";
import "./product-ux/product.css";

const DEFAULT_VIEW: ProductViewId = "task";

export default function App() {
  const [currentView, setCurrentView] = useState<ProductViewId>(DEFAULT_VIEW);
  const [selectedTaskId, setSelectedTaskId] = useState(productExperience.tasks[0]?.id ?? "");
  const activeTask = productExperience.tasks.find((task) => task.id === selectedTaskId) ?? productExperience.tasks[0];

  const handleSelectTask = (taskId: string) => {
    setSelectedTaskId(taskId);
    setCurrentView("task");
  };

  if (!activeTask) {
    return null;
  }

  return (
    <AppShell
      currentTask={activeTask}
      currentView={currentView}
      onSelectTask={handleSelectTask}
      onViewChange={setCurrentView}
      product={productExperience}
    >
      {currentView === "workboard" ? (
        <TaskInboxWorkboardScreen onOpenTask={handleSelectTask} product={productExperience} task={activeTask} />
      ) : null}
      {currentView === "task" ? (
        <TaskDetailScreen
          onOpenContext={() => setCurrentView("context")}
          onOpenHandoff={() => setCurrentView("handoff")}
          product={productExperience}
          task={activeTask}
        />
      ) : null}
      {currentView === "handoff" ? (
        <AgentHandoffScreen onOpenReview={() => setCurrentView("review")} product={productExperience} task={activeTask} />
      ) : null}
      {currentView === "review" ? (
        <ReviewResultScreen onOpenTask={() => setCurrentView("task")} product={productExperience} task={activeTask} />
      ) : null}
      {currentView === "context" ? (
        <ContextViewScreen onOpenTask={() => setCurrentView("task")} product={productExperience} task={activeTask} />
      ) : null}
    </AppShell>
  );
}

