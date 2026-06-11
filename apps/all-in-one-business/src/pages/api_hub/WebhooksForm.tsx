import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const WebhooksForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="api_hub" 
      entity="webhooks" 
      type="form" 
      title="Webhooks" 
    />
  );
};

export default WebhooksForm;
