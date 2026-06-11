import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const PropertiesList: React.FC = () => {
  return (
    <SmartCRUD 
      module="property" 
      entity="properties" 
      type="list" 
      title="Properties" 
    />
  );
};

export default PropertiesList;
