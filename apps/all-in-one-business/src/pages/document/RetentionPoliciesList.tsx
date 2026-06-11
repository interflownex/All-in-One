import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const RetentionPoliciesList: React.FC = () => {
  return (
    <SmartCRUD 
      module="document" 
      entity="retentionpolicies" 
      type="list" 
      title="Retention Policies" 
    />
  );
};

export default RetentionPoliciesList;
