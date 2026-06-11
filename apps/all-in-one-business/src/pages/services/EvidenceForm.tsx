import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const EvidenceForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="services" 
      entity="evidence" 
      type="form" 
      title="Evidence" 
    />
  );
};

export default EvidenceForm;
