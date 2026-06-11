import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const PermissionsPermissions: React.FC = () => {
  return (
    <SmartCRUD 
      module="permissions" 
      entity="permissionspermissions" 
      type="list" 
      title="Permissões Permissões" 
    />
  );
};

export default PermissionsPermissions;
