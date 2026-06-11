import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const AssembliesList: React.FC = () => {
  return (
    <SmartCRUD 
      module="property" 
      entity="assemblies" 
      type="list" 
      title="Assemblies" 
    />
  );
};

export default AssembliesList;
