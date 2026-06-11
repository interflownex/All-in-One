import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const StoresList: React.FC = () => {
  return (
    <SmartCRUD 
      module="marketplace" 
      entity="stores" 
      type="list" 
      title="Stores" 
    />
  );
};

export default StoresList;
