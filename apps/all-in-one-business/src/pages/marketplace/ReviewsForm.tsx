import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const ReviewsForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="marketplace" 
      entity="reviews" 
      type="form" 
      title="Reviews" 
    />
  );
};

export default ReviewsForm;
