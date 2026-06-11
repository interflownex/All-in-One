import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const PatientsForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="health" 
      entity="patients" 
      type="form" 
      title="Patients" 
    />
  );
};

export default PatientsForm;
