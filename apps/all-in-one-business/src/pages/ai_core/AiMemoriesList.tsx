import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const AiMemoriesList: React.FC = () => {
  return <SmartCRUD module="ai_core" entity="aimemories" type="list" title="Ai Memories" />;
};

export default AiMemoriesList;
