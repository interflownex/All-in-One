import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const ActivitiesForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="crm" 
      entity="activities" 
      type="form" 
      title="Activities" 
    />
  );
};

export default ActivitiesForm;
