import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const CandidatesForm: React.FC = () => {
  return (
    <SmartCRUD 
      module="hr" 
      entity="candidates" 
      type="form" 
      title="Candidates" 
    />
  );
};

export default CandidatesForm;
