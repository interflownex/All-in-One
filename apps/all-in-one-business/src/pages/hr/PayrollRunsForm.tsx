import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const PayrollRunsForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="hr" 
      entity="payrollruns" 
      type="form" 
      title="Payroll Runs" 
    />
  );
};

export default PayrollRunsForm;
