import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const KybBusiness: React.FC = () => {
  return (
    <SmartCRUD 
      module="identity" 
      entity="kybbusiness" 
      type="form" 
      title="Kyb Business" 
    />
  );
};

export default KybBusiness;
