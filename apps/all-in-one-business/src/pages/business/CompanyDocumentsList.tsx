import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const CompanyDocumentsList: React.FC = () => {
  return (
    <SmartCRUD 
      module="business" 
      entity="companydocuments" 
      type="list" 
      title="Company Documents" 
    />
  );
};

export default CompanyDocumentsList;
