import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const CostCentersList: React.FC = () => {
  return (
    <SmartCRUD 
      module="erp" 
      entity="costcenters" 
      type="list" 
      title="Cost Centers" 
    />
  );
};

export default CostCentersList;
