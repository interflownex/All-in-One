import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const EmploymentRecordsForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="jobs" 
      entity="employmentrecords" 
      type="form" 
      title="Employment Records" 
    />
  );
};

export default EmploymentRecordsForm;
