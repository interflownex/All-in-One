import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const BinsForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="wms" 
      entity="bins" 
      type="form" 
      title="Bins" 
    />
  );
};

export default BinsForm;
