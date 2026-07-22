import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const Api_hubOverview: React.FC = () => {
  return <SmartCRUD module="api_hub" entity="api_hub" type="list" title="Api_hub" />;
};

export default Api_hubOverview;
