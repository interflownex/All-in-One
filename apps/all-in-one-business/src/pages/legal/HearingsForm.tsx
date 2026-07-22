import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const HearingsForm: React.FC = () => {
  return <SmartCRUD module="legal" entity="hearings" type="form" title="Hearings" />;
};

export default HearingsForm;
