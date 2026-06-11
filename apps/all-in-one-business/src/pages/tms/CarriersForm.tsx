import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const CarriersForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="tms" 
      entity="carriers" 
      type="form" 
      title="Carriers" 
    />
  );
};

export default CarriersForm;
