import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const ExportsForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="bi" 
      entity="exports" 
      type="form" 
      title="Exports" 
    />
  );
};

export default ExportsForm;
