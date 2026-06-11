import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const CatalogOffersForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="business" 
      entity="catalogoffers" 
      type="form" 
      title="Catalog Offers" 
    />
  );
};

export default CatalogOffersForm;
