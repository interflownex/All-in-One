import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const PropertiesForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="property" 
      entity="properties" 
      type="form" 
      title="Properties" 
    />
  );
};

export default PropertiesForm;
