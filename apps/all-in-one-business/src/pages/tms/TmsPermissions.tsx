import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const TmsPermissions: React.FC = () => {
  return (
    <SmartCRUD 
      module="tms" 
      entity="tmspermissions" 
      type="list" 
      title="Tms Permissões" 
    />
  );
};

export default TmsPermissions;
