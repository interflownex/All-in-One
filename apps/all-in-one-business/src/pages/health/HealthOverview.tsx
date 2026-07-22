import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const HealthOverview: React.FC = () => {
  return <SmartCRUD module="health" entity="health" type="list" title="Health" />;
};

export default HealthOverview;
