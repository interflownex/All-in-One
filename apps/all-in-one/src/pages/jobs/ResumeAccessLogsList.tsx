import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const ResumeAccessLogsList: React.FC = () => {
  return (
    <SmartCRUD module="jobs" entity="resumeaccesslogs" type="list" title="Resume Access Logs" />
  );
};

export default ResumeAccessLogsList;
