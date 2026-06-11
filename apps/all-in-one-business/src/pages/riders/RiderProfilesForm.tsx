import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const RiderProfilesForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="riders" 
      entity="riderprofiles" 
      type="form" 
      title="Rider Profiles" 
    />
  );
};

export default RiderProfilesForm;
