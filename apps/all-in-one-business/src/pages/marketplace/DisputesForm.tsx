import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const DisputesForm: React.FC = () => {
  return <SmartCRUD module="marketplace" entity="disputes" type="form" title="Disputes" />;
};

export default DisputesForm;
