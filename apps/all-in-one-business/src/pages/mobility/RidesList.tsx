import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const RidesList: React.FC = () => {
  return (
    <SmartCRUD 
      module="mobility" 
      entity="rides" 
      type="list" 
      title="Rides" 
    />
  );
};

export default RidesList;
