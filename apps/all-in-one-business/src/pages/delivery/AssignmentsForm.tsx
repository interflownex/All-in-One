import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const AssignmentsForm: React.FC = () => {
  return <SmartCRUD module="delivery" entity="assignments" type="form" title="Assignments" />;
};

export default AssignmentsForm;
