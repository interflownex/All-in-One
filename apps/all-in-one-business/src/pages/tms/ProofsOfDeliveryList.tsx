import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const ProofsOfDeliveryList: React.FC = () => {
  return (
    <SmartCRUD 
      module="tms" 
      entity="proofsofdelivery" 
      type="list" 
      title="Proofs Of Delivery" 
    />
  );
};

export default ProofsOfDeliveryList;
