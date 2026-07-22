import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const ApiClientsList: React.FC = () => {
  return <SmartCRUD module="api_hub" entity="apiclients" type="list" title="Api Clients" />;
};

export default ApiClientsList;
