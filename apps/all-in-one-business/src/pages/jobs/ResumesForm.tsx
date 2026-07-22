import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const ResumesForm: React.FC = () => {
  return <SmartCRUD module="jobs" entity="resumes" type="form" title="Resumes" />;
};

export default ResumesForm;
