import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const StopsForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="mobility" 
      entity="stops" 
      type="form" 
      title="Stops" 
    />
  );
};

export default StopsForm;
