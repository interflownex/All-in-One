import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const ProofsForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="delivery" 
      entity="proofs" 
      type="form" 
      title="Proofs" 
    />
  );
};

export default ProofsForm;
