import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const RidersPermissions: React.FC = () => {
  return (
    <SmartCRUD 
      module="riders" 
      entity="riderspermissions" 
      type="list" 
      title="Riders Permissões" 
    />
  );
};

export default RidersPermissions;
