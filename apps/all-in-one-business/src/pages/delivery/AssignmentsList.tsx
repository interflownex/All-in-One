import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const AssignmentsList: React.FC = () => {
  return (
    <SmartCRUD 
      module="delivery" 
      entity="assignments" 
      type="list" 
      title="Assignments" 
    />
  );
};

export default AssignmentsList;
