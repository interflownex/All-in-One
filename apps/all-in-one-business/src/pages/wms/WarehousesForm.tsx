import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const WarehousesForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="wms" 
      entity="warehouses" 
      type="form" 
      title="Warehouses" 
    />
  );
};

export default WarehousesForm;
