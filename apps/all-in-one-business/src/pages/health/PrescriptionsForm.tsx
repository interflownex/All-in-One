import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const PrescriptionsForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="health" 
      entity="prescriptions" 
      type="form" 
      title="Prescriptions" 
    />
  );
};

export default PrescriptionsForm;
