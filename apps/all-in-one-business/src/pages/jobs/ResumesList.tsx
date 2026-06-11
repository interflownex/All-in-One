import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const ResumesList: React.FC = () => {
  return (
    <SmartCRUD 
      module="jobs" 
      entity="resumes" 
      type="list" 
      title="Resumes" 
    />
  );
};

export default ResumesList;
