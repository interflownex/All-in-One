import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const UsersForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="identity" 
      entity="users" 
      type="form" 
      title="Users" 
    />
  );
};

export default UsersForm;
