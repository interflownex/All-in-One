import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const VersionsForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="document" 
      entity="versions" 
      type="form" 
      title="Versions" 
    />
  );
};

export default VersionsForm;
