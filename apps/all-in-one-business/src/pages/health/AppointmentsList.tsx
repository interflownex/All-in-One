import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const AppointmentsList: React.FC = () => {
  return (
    <SmartCRUD 
      module="health" 
      entity="appointments" 
      type="list" 
      title="Appointments" 
    />
  );
};

export default AppointmentsList;
