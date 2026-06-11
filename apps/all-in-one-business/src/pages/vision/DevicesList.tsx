import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const DevicesList: React.FC = () => {
  return (
    <SmartCRUD 
      module="vision" 
      entity="devices" 
      type="list" 
      title="Devices" 
    />
  );
};

export default DevicesList;
