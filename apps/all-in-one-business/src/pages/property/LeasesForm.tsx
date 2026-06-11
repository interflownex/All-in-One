import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const LeasesForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="property" 
      entity="leases" 
      type="form" 
      title="Leases" 
    />
  );
};

export default LeasesForm;
