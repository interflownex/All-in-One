import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const FiscalDocumentsForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="erp" 
      entity="fiscaldocuments" 
      type="form" 
      title="Fiscal Documents" 
    />
  );
};

export default FiscalDocumentsForm;
