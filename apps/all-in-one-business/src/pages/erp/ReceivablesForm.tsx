import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const ReceivablesForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="erp" 
      entity="receivables" 
      type="form" 
      title="Receivables" 
    />
  );
};

export default ReceivablesForm;
