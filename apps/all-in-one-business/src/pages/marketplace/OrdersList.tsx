import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const OrdersList: React.FC = () => {
  return (
    <SmartCRUD 
      module="marketplace" 
      entity="orders" 
      type="list" 
      title="Orders" 
    />
  );
};

export default OrdersList;
