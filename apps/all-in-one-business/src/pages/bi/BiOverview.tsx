import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const BiOverview: React.FC = () => {
  return (
    <SmartCRUD 
      module="bi" 
      entity="bi" 
      type="list" 
      title="Bi" 
    />
  );
};

export default BiOverview;
