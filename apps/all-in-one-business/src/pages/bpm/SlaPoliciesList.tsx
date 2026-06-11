import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const SlaPoliciesList: React.FC = () => {
  return (
    <SmartCRUD 
      module="bpm" 
      entity="slapolicies" 
      type="list" 
      title="Sla Policies" 
    />
  );
};

export default SlaPoliciesList;
