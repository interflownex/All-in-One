import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const ApiClientsForm: React.FC = () => {
  return <SmartCRUD module="api_hub" entity="apiclients" type="form" title="Api Clients" />;
};

export default ApiClientsForm;
