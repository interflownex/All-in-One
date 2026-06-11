import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const RidesForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="mobility" 
      entity="rides" 
      type="form" 
      title="Rides" 
    />
  );
};

export default RidesForm;
