import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const ModelRunsForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="ai_core" 
      entity="modelruns" 
      type="form" 
      title="Model Runs" 
    />
  );
};

export default ModelRunsForm;
