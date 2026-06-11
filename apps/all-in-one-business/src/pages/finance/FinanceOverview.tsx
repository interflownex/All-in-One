import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const FinanceOverview: React.FC = () => {
  return (
    <SmartCRUD 
      module="finance" 
      entity="finance" 
      type="list" 
      title="Finance" 
    />
  );
};

export default FinanceOverview;
