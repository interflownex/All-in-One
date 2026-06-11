import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const DeliveryPermissions: React.FC = () => {
  return (
    <SmartCRUD 
      module="delivery" 
      entity="deliverypermissions" 
      type="list" 
      title="Delivery Permissões" 
    />
  );
};

export default DeliveryPermissions;
