import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const ProductsList: React.FC = () => {
  return (
    <SmartCRUD 
      module="marketplace" 
      entity="products" 
      type="list" 
      title="Products" 
    />
  );
};

export default ProductsList;
