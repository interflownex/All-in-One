import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const Api_hubPermissions: React.FC = () => {
  return (
    <SmartCRUD 
      module="api_hub" 
      entity="api_hubpermissions" 
      type="list" 
      title="Api_hub Permissões" 
    />
  );
};

export default Api_hubPermissions;
