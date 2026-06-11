import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const BedsForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="health" 
      entity="beds" 
      type="form" 
      title="Beds" 
    />
  );
};

export default BedsForm;
