import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const ServicesPermissions: React.FC = () => {
  return (
    <SmartCRUD 
      module="services" 
      entity="servicespermissions" 
      type="list" 
      title="Services Permissões" 
    />
  );
};

export default ServicesPermissions;
