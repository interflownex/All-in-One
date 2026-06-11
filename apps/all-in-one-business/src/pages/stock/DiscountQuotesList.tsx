import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const DiscountQuotesList: React.FC = () => {
  return (
    <SmartCRUD 
      module="stock" 
      entity="discountquotes" 
      type="list" 
      title="Discount Quotes" 
    />
  );
};

export default DiscountQuotesList;
