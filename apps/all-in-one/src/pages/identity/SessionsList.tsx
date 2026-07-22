import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const SessionsList: React.FC = () => {
  return <SmartCRUD module="identity" entity="sessions" type="list" title="Sessions" />;
};

export default SessionsList;
