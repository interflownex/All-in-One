import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const CasesForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="legal" 
      entity="cases" 
      type="form" 
      title="Cases" 
    />
  );
};

export default CasesForm;
