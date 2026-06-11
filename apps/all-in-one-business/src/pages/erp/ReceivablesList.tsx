import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const ReceivablesList: React.FC = () => {
  return (
    <SmartCRUD 
      module="erp" 
      entity="receivables" 
      type="list" 
      title="Receivables" 
    />
  );
};

export default ReceivablesList;
