import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const HearingsList: React.FC = () => {
  return <SmartCRUD module="legal" entity="hearings" type="list" title="Hearings" />;
};

export default HearingsList;
