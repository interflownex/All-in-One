import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const SlaPoliciesForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="bpm" 
      entity="slapolicies" 
      type="form" 
      title="Sla Policies" 
    />
  );
};

export default SlaPoliciesForm;
