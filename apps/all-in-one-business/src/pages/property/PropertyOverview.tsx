import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const PropertyOverview: React.FC = () => {
  return (
    <SmartCRUD 
      module="property" 
      entity="property" 
      type="list" 
      title="Property" 
    />
  );
};

export default PropertyOverview;
