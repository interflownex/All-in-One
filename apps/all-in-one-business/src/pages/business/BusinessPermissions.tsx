import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const BusinessPermissions: React.FC = () => {
  return (
    <SmartCRUD 
      module="business" 
      entity="businesspermissions" 
      type="list" 
      title="Business Permissões" 
    />
  );
};

export default BusinessPermissions;
