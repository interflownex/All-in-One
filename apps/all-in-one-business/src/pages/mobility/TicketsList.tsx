import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const TicketsList: React.FC = () => {
  return (
    <SmartCRUD 
      module="mobility" 
      entity="tickets" 
      type="list" 
      title="Tickets" 
    />
  );
};

export default TicketsList;
