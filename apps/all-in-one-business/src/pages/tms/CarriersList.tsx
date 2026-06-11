import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const CarriersList: React.FC = () => {
  return (
    <SmartCRUD 
      module="tms" 
      entity="carriers" 
      type="list" 
      title="Carriers" 
    />
  );
};

export default CarriersList;
