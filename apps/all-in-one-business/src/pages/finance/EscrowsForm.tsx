import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const EscrowsForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="finance" 
      entity="escrows" 
      type="form" 
      title="Escrows" 
    />
  );
};

export default EscrowsForm;
