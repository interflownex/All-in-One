import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const HrOverview: React.FC = () => {
  return <SmartCRUD module="hr" entity="hr" type="list" title="Hr" />;
};

export default HrOverview;
