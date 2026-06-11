import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const ResumeDocumentsForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="jobs" 
      entity="resumedocuments" 
      type="form" 
      title="Resume Documents" 
    />
  );
};

export default ResumeDocumentsForm;
