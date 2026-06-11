import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const InventoryList: React.FC = () => {
  return (
    <SmartCRUD 
      module="wms" 
      entity="inventory" 
      type="list" 
      title="Inventory" 
    />
  );
};

export default InventoryList;
