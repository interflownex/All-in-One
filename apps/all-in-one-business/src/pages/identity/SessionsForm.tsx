import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const SessionsForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="identity" 
      entity="sessions" 
      type="form" 
      title="Sessions" 
    />
  );
};

export default SessionsForm;
