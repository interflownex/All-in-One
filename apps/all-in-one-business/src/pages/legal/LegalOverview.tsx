import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const LegalOverview: React.FC = () => {
  return <SmartCRUD module="legal" entity="legal" type="list" title="Legal" />;
};

export default LegalOverview;
