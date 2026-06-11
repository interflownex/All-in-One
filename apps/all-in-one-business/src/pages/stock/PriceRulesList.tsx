import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const PriceRulesList: React.FC = () => {
  return (
    <SmartCRUD 
      module="stock" 
      entity="pricerules" 
      type="list" 
      title="Price Rules" 
    />
  );
};

export default PriceRulesList;
