import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const IdentityOverview: React.FC = () => {
  return (
    <SmartCRUD 
      module="identity" 
      entity="identity" 
      type="list" 
      title="Identity" 
    />
  );
};

export default IdentityOverview;
