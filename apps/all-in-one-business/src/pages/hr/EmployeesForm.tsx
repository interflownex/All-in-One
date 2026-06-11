import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const EmployeesForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="hr" 
      entity="employees" 
      type="form" 
      title="Employees" 
    />
  );
};

export default EmployeesForm;
