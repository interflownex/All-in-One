import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const VehiclesForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="riders" 
      entity="vehicles" 
      type="form" 
      title="Vehicles" 
    />
  );
};

export default VehiclesForm;
