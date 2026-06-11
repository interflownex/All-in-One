import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const ProcessesForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="bpm" 
      entity="processes" 
      type="form" 
      title="Processes" 
    />
  );
};

export default ProcessesForm;
