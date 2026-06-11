import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const ServiceContractsForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="services" 
      entity="servicecontracts" 
      type="form" 
      title="Service Contracts" 
    />
  );
};

export default ServiceContractsForm;
