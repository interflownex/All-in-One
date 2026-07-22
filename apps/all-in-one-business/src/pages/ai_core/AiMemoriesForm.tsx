import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const AiMemoriesForm: React.FC = () => {
  return <SmartCRUD module="ai_core" entity="aimemories" type="form" title="Ai Memories" />;
};

export default AiMemoriesForm;
