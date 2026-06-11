import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const RoutesForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="mobility" 
      entity="routes" 
      type="form" 
      title="Routes" 
    />
  );
};

export default RoutesForm;
