import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const PermissionsForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="permissions" 
      entity="permissions" 
      type="list" 
      title="Permissões" 
    />
  );
};

export default PermissionsForm;
