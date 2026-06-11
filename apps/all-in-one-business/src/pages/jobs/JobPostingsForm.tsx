import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const JobPostingsForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="jobs" 
      entity="jobpostings" 
      type="form" 
      title="Job Postings" 
    />
  );
};

export default JobPostingsForm;
