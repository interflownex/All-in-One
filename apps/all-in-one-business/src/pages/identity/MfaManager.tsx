import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const MfaManager: React.FC = () => {
  return (
    <SmartCRUD 
      module="identity" 
      entity="mfamanager" 
      type="form" 
      title="Mfa Manager" 
    />
  );
};

export default MfaManager;
