import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const DevicesForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="vision" 
      entity="devices" 
      type="form" 
      title="Devices" 
    />
  );
};

export default DevicesForm;
