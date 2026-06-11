import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const RidersOverview: React.FC = () => {
  return (
    <SmartCRUD 
      module="riders" 
      entity="riders" 
      type="list" 
      title="Riders" 
    />
  );
};

export default RidersOverview;
