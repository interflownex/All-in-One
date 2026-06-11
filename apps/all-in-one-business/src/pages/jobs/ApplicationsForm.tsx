import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const ApplicationsForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="jobs" 
      entity="applications" 
      type="form" 
      title="Applications" 
    />
  );
};

export default ApplicationsForm;
