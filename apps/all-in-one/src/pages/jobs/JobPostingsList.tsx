import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const JobPostingsList: React.FC = () => {
  return <SmartCRUD module="jobs" entity="jobpostings" type="list" title="Job Postings" />;
};

export default JobPostingsList;
