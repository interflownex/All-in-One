import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const DiscountQuotesForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="stock" 
      entity="discountquotes" 
      type="form" 
      title="Discount Quotes" 
    />
  );
};

export default DiscountQuotesForm;
