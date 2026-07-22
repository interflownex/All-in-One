import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const ModelRunsList: React.FC = () => {
  return <SmartCRUD module="ai_core" entity="modelruns" type="list" title="Model Runs" />;
};

export default ModelRunsList;
