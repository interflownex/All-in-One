import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const LegalContractsList: React.FC = () => {
  return (
    <SmartCRUD 
      module="legal" 
      entity="legalcontracts" 
      type="list" 
      title="Legal Contracts" 
    />
  );
};

export default LegalContractsList;
