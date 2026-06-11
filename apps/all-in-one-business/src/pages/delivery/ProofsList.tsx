import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const ProofsList: React.FC = () => {
  return (
    <SmartCRUD 
      module="delivery" 
      entity="proofs" 
      type="list" 
      title="Proofs" 
    />
  );
};

export default ProofsList;
