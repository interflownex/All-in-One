import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const MobilityOverview: React.FC = () => {
  return (
    <SmartCRUD 
      module="mobility" 
      entity="mobility" 
      type="list" 
      title="Mobility" 
    />
  );
};

export default MobilityOverview;
