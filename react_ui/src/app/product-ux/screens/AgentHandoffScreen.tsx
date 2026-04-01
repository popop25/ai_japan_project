import { HandoffComposer } from "../components/HandoffComposer";
import { HandoffMode, TaskActionId, TaskRecord } from "../types";

interface AgentHandoffScreenProps {
  onChangeHandoffMode: (mode: HandoffMode) => void;
  onOpenContext: () => void;
  onTriggerAction: (actionId: TaskActionId) => void;
  task: TaskRecord;
}

export function AgentHandoffScreen({ onChangeHandoffMode, onOpenContext, onTriggerAction, task }: AgentHandoffScreenProps) {
  return <HandoffComposer onChangeHandoffMode={onChangeHandoffMode} onOpenContext={onOpenContext} onTriggerAction={onTriggerAction} task={task} />;
}
