import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const WorkflowInstancesList: React.FC = () => {
  return (
    <SmartCRUD module="bpm" entity="workflowinstances" type="list" title="Workflow Instances" />
  );
};

export default WorkflowInstancesList;
