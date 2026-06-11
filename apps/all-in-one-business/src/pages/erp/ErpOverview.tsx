import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const ErpOverview: React.FC = () => {
  return (
    <SmartCRUD 
      module="erp" 
      entity="erp" 
      type="list" 
      title="Erp" 
    />
  );
};

export default ErpOverview;
