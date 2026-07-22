import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const FreightsForm: React.FC = () => {
  return <SmartCRUD module="tms" entity="freights" type="form" title="Freights" />;
};

export default FreightsForm;
