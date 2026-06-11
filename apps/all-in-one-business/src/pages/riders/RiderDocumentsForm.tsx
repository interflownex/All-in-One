import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const RiderDocumentsForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="riders" 
      entity="riderdocuments" 
      type="form" 
      title="Rider Documents" 
    />
  );
};

export default RiderDocumentsForm;
