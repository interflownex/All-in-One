import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const RolesForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="permissions" 
      entity="roles" 
      type="form" 
      title="Roles" 
    />
  );
};

export default RolesForm;
