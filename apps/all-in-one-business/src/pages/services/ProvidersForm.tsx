import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const ProvidersForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="services" 
      entity="providers" 
      type="form" 
      title="Providers" 
    />
  );
};

export default ProvidersForm;
