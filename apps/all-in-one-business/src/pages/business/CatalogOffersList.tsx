import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const CatalogOffersList: React.FC = () => {
  return (
    <SmartCRUD 
      module="business" 
      entity="catalogoffers" 
      type="list" 
      title="Catalog Offers" 
    />
  );
};

export default CatalogOffersList;
