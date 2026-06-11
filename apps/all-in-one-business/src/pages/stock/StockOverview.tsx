import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const StockOverview: React.FC = () => {
  return (
    <SmartCRUD 
      module="stock" 
      entity="stock" 
      type="list" 
      title="Stock" 
    />
  );
};

export default StockOverview;
