import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const CartsList: React.FC = () => {
  return (
    <SmartCRUD 
      module="marketplace" 
      entity="carts" 
      type="list" 
      title="Carts" 
    />
  );
};

export default CartsList;
