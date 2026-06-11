import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const FinancePermissions: React.FC = () => {
  return (
    <SmartCRUD 
      module="finance" 
      entity="financepermissions" 
      type="list" 
      title="Finance Permissões" 
    />
  );
};

export default FinancePermissions;
