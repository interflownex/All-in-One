import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const CandidateResume: React.FC = () => {
  return <SmartCRUD module="jobs" entity="candidateresume" type="form" title="Candidate Resume" />;
};

export default CandidateResume;
