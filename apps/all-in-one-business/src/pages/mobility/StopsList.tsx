import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const StopsList: React.FC = () => {
  return (
    <SmartCRUD 
      module="mobility" 
      entity="stops" 
      type="list" 
      title="Stops" 
    />
  );
};

export default StopsList;
