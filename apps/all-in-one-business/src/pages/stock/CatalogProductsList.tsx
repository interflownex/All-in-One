import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const CatalogProductsList: React.FC = () => {
  return (
    <SmartCRUD 
      module="stock" 
      entity="catalogproducts" 
      type="list" 
      title="Catalog Products" 
    />
  );
};

export default CatalogProductsList;
