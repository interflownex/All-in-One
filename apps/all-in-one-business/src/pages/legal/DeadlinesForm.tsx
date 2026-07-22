import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const DeadlinesForm: React.FC = () => {
  return <SmartCRUD module="legal" entity="deadlines" type="form" title="Deadlines" />;
};

export default DeadlinesForm;
