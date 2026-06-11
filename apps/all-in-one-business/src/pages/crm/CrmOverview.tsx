import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const CrmOverview: React.FC = () => {
  return (
    <SmartCRUD 
      module="crm" 
      entity="crm" 
      type="list" 
      title="Crm" 
    />
  );
};

export default CrmOverview;
