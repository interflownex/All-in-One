import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const ResumeDocumentsList: React.FC = () => {
  return (
    <SmartCRUD 
      module="jobs" 
      entity="resumedocuments" 
      type="list" 
      title="Resume Documents" 
    />
  );
};

export default ResumeDocumentsList;
