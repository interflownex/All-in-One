import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const UserRolesForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="permissions" 
      entity="userroles" 
      type="form" 
      title="User Roles" 
    />
  );
};

export default UserRolesForm;
