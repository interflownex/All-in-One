import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const EmploymentRecordsList: React.FC = () => {
  return (
    <SmartCRUD 
      module="jobs" 
      entity="employmentrecords" 
      type="list" 
      title="Employment Records" 
    />
  );
};

export default EmploymentRecordsList;
