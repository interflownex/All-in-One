import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const PropertyPermissions: React.FC = () => {
  return (
    <SmartCRUD 
      module="property" 
      entity="propertypermissions" 
      type="list" 
      title="Property Permissões" 
    />
  );
};

export default PropertyPermissions;
