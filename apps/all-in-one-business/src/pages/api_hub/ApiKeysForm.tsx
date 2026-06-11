import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const ApiKeysForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="api_hub" 
      entity="apikeys" 
      type="form" 
      title="Api Keys" 
    />
  );
};

export default ApiKeysForm;
