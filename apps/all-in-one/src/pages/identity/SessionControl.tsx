import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const SessionControl: React.FC = () => {
  return (
    <SmartCRUD module="identity" entity="sessioncontrol" type="form" title="Session Control" />
  );
};

export default SessionControl;
