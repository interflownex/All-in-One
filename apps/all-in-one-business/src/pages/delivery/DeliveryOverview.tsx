import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const DeliveryOverview: React.FC = () => {
  return (
    <SmartCRUD 
      module="delivery" 
      entity="delivery" 
      type="list" 
      title="Delivery" 
    />
  );
};

export default DeliveryOverview;
