import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const BpmPermissions: React.FC = () => {
  return (
    <SmartCRUD 
      module="bpm" 
      entity="bpmpermissions" 
      type="list" 
      title="Bpm Permissões" 
    />
  );
};

export default BpmPermissions;
