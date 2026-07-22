import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const RecruiterResumeReview: React.FC = () => {
  return (
    <SmartCRUD
      module="jobs"
      entity="recruiterresumereview"
      type="form"
      title="Recruiter Resume Review"
    />
  );
};

export default RecruiterResumeReview;
