import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const ApplicationsList: React.FC = () => {
  return (
    <SmartCRUD 
      module="jobs" 
      entity="applications" 
      type="list" 
      title="Applications" 
    />
  );
};

export default ApplicationsList;
