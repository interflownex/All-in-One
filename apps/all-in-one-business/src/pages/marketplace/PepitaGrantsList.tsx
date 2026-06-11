import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const PepitaGrantsList: React.FC = () => {
  return (
    <SmartCRUD 
      module="marketplace" 
      entity="pepitagrants" 
      type="list" 
      title="Pepita Grants" 
    />
  );
};

export default PepitaGrantsList;
