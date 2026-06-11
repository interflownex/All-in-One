import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const BiometricsList: React.FC = () => {
  return (
    <SmartCRUD 
      module="identity" 
      entity="biometrics" 
      type="list" 
      title="Biometrics" 
    />
  );
};

export default BiometricsList;
