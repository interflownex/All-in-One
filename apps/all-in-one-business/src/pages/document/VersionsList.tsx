import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const VersionsList: React.FC = () => {
  return (
    <SmartCRUD 
      module="document" 
      entity="versions" 
      type="list" 
      title="Versions" 
    />
  );
};

export default VersionsList;
