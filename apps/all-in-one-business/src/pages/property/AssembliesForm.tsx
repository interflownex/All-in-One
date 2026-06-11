import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const AssembliesForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="property" 
      entity="assemblies" 
      type="form" 
      title="Assemblies" 
    />
  );
};

export default AssembliesForm;
