import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const MaintenanceOrdersForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="property" 
      entity="maintenanceorders" 
      type="form" 
      title="Maintenance Orders" 
    />
  );
};

export default MaintenanceOrdersForm;
