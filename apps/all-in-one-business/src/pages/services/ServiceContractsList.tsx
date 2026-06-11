import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const ServiceContractsList: React.FC = () => {
  return (
    <SmartCRUD 
      module="services" 
      entity="servicecontracts" 
      type="list" 
      title="Service Contracts" 
    />
  );
};

export default ServiceContractsList;
