import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const IdentityVerificationsForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="identity" 
      entity="identityverifications" 
      type="form" 
      title="Identity Verifications" 
    />
  );
};

export default IdentityVerificationsForm;
