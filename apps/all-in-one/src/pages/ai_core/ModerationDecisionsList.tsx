import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const ModerationDecisionsList: React.FC = () => {
  return (
    <SmartCRUD
      module="ai_core"
      entity="moderationdecisions"
      type="list"
      title="Moderation Decisions"
    />
  );
};

export default ModerationDecisionsList;
