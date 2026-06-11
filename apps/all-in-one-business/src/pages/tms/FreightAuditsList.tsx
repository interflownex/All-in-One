import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const FreightAuditsList: React.FC = () => {
  return (
    <SmartCRUD 
      module="tms" 
      entity="freightaudits" 
      type="list" 
      title="Freight Audits" 
    />
  );
};

export default FreightAuditsList;
