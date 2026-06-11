import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const RiderReviewsForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="riders" 
      entity="riderreviews" 
      type="form" 
      title="Rider Reviews" 
    />
  );
};

export default RiderReviewsForm;
