import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const DocumentPermissions: React.FC = () => {
  return (
    <SmartCRUD 
      module="document" 
      entity="documentpermissions" 
      type="list" 
      title="Document Permissões" 
    />
  );
};

export default DocumentPermissions;
