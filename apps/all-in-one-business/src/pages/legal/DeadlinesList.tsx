import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const DeadlinesList: React.FC = () => {
  return <SmartCRUD module="legal" entity="deadlines" type="list" title="Deadlines" />;
};

export default DeadlinesList;
