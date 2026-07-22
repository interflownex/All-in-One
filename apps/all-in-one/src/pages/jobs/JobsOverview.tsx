import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const JobsOverview: React.FC = () => {
  return <SmartCRUD module="jobs" entity="jobs" type="list" title="Jobs" />;
};

export default JobsOverview;
