import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const CandidatesList: React.FC = () => {
  return (
    <SmartCRUD 
      module="hr" 
      entity="candidates" 
      type="list" 
      title="Candidates" 
    />
  );
};

export default CandidatesList;
