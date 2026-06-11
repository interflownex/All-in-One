import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const AuthGateway: React.FC = () => {
  return (
    <SmartCRUD 
      module="identity" 
      entity="authgateway" 
      type="form" 
      title="Auth Gateway" 
    />
  );
};

export default AuthGateway;
