import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const ErpPermissions: React.FC = () => {
  return (
    <SmartCRUD 
      module="erp" 
      entity="erppermissions" 
      type="list" 
      title="Erp Permissões" 
    />
  );
};

export default ErpPermissions;
