import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const ResumeAccessLogsForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="jobs" 
      entity="resumeaccesslogs" 
      type="form" 
      title="Resume Access Logs" 
    />
  );
};

export default ResumeAccessLogsForm;
