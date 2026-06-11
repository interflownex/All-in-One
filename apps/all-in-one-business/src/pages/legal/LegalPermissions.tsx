import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const LegalPermissions: React.FC = () => {
  return (
    <SmartCRUD 
      module="legal" 
      entity="legalpermissions" 
      type="list" 
      title="Legal Permissões" 
    />
  );
};

export default LegalPermissions;
