import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const IntegrationRunsList: React.FC = () => {
  return (
    <SmartCRUD module="api_hub" entity="integrationruns" type="list" title="Integration Runs" />
  );
};

export default IntegrationRunsList;
