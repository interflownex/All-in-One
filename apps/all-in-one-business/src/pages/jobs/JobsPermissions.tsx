import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const JobsPermissions: React.FC = () => {
  return (
    <SmartCRUD 
      module="jobs" 
      entity="jobspermissions" 
      type="list" 
      title="Jobs Permissões" 
    />
  );
};

export default JobsPermissions;
