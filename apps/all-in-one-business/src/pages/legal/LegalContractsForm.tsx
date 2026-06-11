import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const LegalContractsForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="legal" 
      entity="legalcontracts" 
      type="form" 
      title="Legal Contracts" 
    />
  );
};

export default LegalContractsForm;
