import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const BedsList: React.FC = () => {
  return (
    <SmartCRUD 
      module="health" 
      entity="beds" 
      type="list" 
      title="Beds" 
    />
  );
};

export default BedsList;
