import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const IntegrationRunsForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="api_hub" 
      entity="integrationruns" 
      type="form" 
      title="Integration Runs" 
    />
  );
};

export default IntegrationRunsForm;
