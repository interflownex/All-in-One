import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const BpmOverview: React.FC = () => {
  return (
    <SmartCRUD 
      module="bpm" 
      entity="bpm" 
      type="list" 
      title="Bpm" 
    />
  );
};

export default BpmOverview;
