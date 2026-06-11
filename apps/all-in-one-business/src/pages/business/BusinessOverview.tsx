import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const BusinessOverview: React.FC = () => {
  return (
    <SmartCRUD 
      module="business" 
      entity="business" 
      type="list" 
      title="Business" 
    />
  );
};

export default BusinessOverview;
