import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const AccessPoliciesForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="permissions" 
      entity="accesspolicies" 
      type="form" 
      title="Access Policies" 
    />
  );
};

export default AccessPoliciesForm;
