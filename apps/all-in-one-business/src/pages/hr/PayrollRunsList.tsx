import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const PayrollRunsList: React.FC = () => {
  return (
    <SmartCRUD 
      module="hr" 
      entity="payrollruns" 
      type="list" 
      title="Payroll Runs" 
    />
  );
};

export default PayrollRunsList;
