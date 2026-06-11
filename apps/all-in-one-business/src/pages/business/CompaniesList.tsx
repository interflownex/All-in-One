import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const CompaniesList: React.FC = () => {
  return (
    <SmartCRUD 
      module="business" 
      entity="companies" 
      type="list" 
      title="Companies" 
    />
  );
};

export default CompaniesList;
