import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const VisionOverview: React.FC = () => {
  return (
    <SmartCRUD 
      module="vision" 
      entity="vision" 
      type="list" 
      title="Vision" 
    />
  );
};

export default VisionOverview;
