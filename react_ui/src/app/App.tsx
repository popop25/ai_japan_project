import { useState } from "react";

import { AppShell } from "./product-ux/components/AppShell";
import { AgentHandoffScreen } from "./product-ux/screens/AgentHandoffScreen";
import { ReviewResultScreen } from "./product-ux/screens/ReviewResultScreen";
import { TaskDetailScreen } from "./product-ux/screens/TaskDetailScreen";
import { initialProductExperience, performTaskAction, preferredViewForTask, setTaskHandoffMode } from "./product-ux/productData";
import { HandoffMode, ProductViewId, TaskActionId } from "./product-ux/types";
import "./product-ux/product.css";

export default function App() {
  const initialTask = initialProductExperience.tasks.find((task) => task.isPrimaryDemo) ?? initialProductExperience.tasks[0];
  const [product, setProduct] = useState(initialProductExperience);
  const [selectedTaskId, setSelectedTaskId] = useState(initialTask?.id ?? "");
  const [currentView, setCurrentView] = useState<ProductViewId>(initialTask ? preferredViewForTask(initialTask) : "task");
  const [taskPickerOpen, setTaskPickerOpen] = useState(false);
  const [contextOpen, setContextOpen] = useState(false);

  const activeTask = product.tasks.find((task) => task.id === selectedTaskId) ?? product.tasks[0];

  const openPreferredStage = (taskId: string) => {
    const task = product.tasks.find((item) => item.id === taskId) ?? product.tasks[0];
    if (!task) {
      return;
    }

    setCurrentView(preferredViewForTask(task));
  };

  const handleSelectTask = (taskId: string) => {
    setSelectedTaskId(taskId);
    openPreferredStage(taskId);
    setTaskPickerOpen(false);
  };

  const handleTriggerAction = (actionId: TaskActionId) => {
    if (!activeTask) {
      return;
    }

    const result = performTaskAction(product, activeTask.id, actionId);
    setProduct(result.product);
    setCurrentView(result.nextView);
  };

  const handleChangeHandoffMode = (mode: HandoffMode) => {
    if (!activeTask) {
      return;
    }

    setProduct((previous) => setTaskHandoffMode(previous, activeTask.id, mode));
  };

  const handleOpenCurrentStage = () => {
    if (!activeTask) {
      return;
    }

    if (activeTask.displayState === "not_started") {
      handleTriggerAction("prepare_brief");
      return;
    }

    if (activeTask.displayState === "brief_ready") {
      setCurrentView("handoff");
      return;
    }

    setCurrentView(preferredViewForTask(activeTask));
  };

  if (!activeTask) {
    return null;
  }

  return (
    <AppShell
      currentTask={activeTask}
      currentView={currentView}
      onSelectTask={handleSelectTask}
      onContextOpenChange={setContextOpen}
      onTaskPickerOpenChange={setTaskPickerOpen}
      product={product}
      contextOpen={contextOpen}
      taskPickerOpen={taskPickerOpen}
    >
      {currentView === "task" ? (
        <TaskDetailScreen onContinue={handleOpenCurrentStage} task={activeTask} />
      ) : null}

      {currentView === "handoff" ? (
        <AgentHandoffScreen
          onChangeHandoffMode={handleChangeHandoffMode}
          onOpenContext={() => setContextOpen(true)}
          onTriggerAction={handleTriggerAction}
          task={activeTask}
        />
      ) : null}

      {currentView === "review" ? (
        <ReviewResultScreen onOpenContext={() => setContextOpen(true)} onTriggerAction={handleTriggerAction} task={activeTask} />
      ) : null}
    </AppShell>
  );
}
