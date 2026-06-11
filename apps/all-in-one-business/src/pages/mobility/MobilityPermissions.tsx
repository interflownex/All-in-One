import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const MobilityPermissions: React.FC = () => {
  return (
    <SmartCRUD 
      module="mobility" 
      entity="mobilitypermissions" 
      type="list" 
      title="Mobility Permissões" 
    />
  );
};

export default MobilityPermissions;
