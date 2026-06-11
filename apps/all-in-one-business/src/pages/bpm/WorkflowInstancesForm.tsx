import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const WorkflowInstancesForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="bpm" 
      entity="workflowinstances" 
      type="form" 
      title="Workflow Instances" 
    />
  );
};

export default WorkflowInstancesForm;
