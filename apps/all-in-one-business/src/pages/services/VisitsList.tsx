import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const VisitsList: React.FC = () => {
  return (
    <SmartCRUD 
      module="services" 
      entity="visits" 
      type="list" 
      title="Visits" 
    />
  );
};

export default VisitsList;
