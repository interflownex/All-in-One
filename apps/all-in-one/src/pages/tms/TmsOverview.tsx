import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const TmsOverview: React.FC = () => {
  return <SmartCRUD module="tms" entity="tms" type="list" title="Tms" />;
};

export default TmsOverview;
