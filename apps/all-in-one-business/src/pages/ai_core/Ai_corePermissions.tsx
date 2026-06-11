import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const Ai_corePermissions: React.FC = () => {
  return (
    <SmartCRUD 
      module="ai_core" 
      entity="ai_corepermissions" 
      type="list" 
      title="Ai_core Permissões" 
    />
  );
};

export default Ai_corePermissions;
