import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const ProcessesList: React.FC = () => {
  return (
    <SmartCRUD 
      module="bpm" 
      entity="processes" 
      type="list" 
      title="Processes" 
    />
  );
};

export default ProcessesList;
