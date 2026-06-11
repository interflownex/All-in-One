import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const ApiKeysList: React.FC = () => {
  return (
    <SmartCRUD 
      module="api_hub" 
      entity="apikeys" 
      type="list" 
      title="Api Keys" 
    />
  );
};

export default ApiKeysList;
