import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const WarehousesList: React.FC = () => {
  return (
    <SmartCRUD 
      module="wms" 
      entity="warehouses" 
      type="list" 
      title="Warehouses" 
    />
  );
};

export default WarehousesList;
