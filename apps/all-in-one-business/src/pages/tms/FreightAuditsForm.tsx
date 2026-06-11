import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const FreightAuditsForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="tms" 
      entity="freightaudits" 
      type="form" 
      title="Freight Audits" 
    />
  );
};

export default FreightAuditsForm;
