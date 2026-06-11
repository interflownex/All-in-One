import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const EscrowsList: React.FC = () => {
  return (
    <SmartCRUD 
      module="finance" 
      entity="escrows" 
      type="list" 
      title="Escrows" 
    />
  );
};

export default EscrowsList;
