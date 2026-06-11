import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const ApprovalLimitsForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="permissions" 
      entity="approvallimits" 
      type="form" 
      title="Approval Limits" 
    />
  );
};

export default ApprovalLimitsForm;
