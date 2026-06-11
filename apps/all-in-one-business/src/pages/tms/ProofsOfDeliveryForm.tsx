import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const ProofsOfDeliveryForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="tms" 
      entity="proofsofdelivery" 
      type="form" 
      title="Proofs Of Delivery" 
    />
  );
};

export default ProofsOfDeliveryForm;
