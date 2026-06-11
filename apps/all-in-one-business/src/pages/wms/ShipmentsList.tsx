import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const ShipmentsList: React.FC = () => {
  return (
    <SmartCRUD 
      module="wms" 
      entity="shipments" 
      type="list" 
      title="Shipments" 
    />
  );
};

export default ShipmentsList;
