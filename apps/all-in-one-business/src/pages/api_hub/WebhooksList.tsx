import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const WebhooksList: React.FC = () => {
  return <SmartCRUD module="api_hub" entity="webhooks" type="list" title="Webhooks" />;
};

export default WebhooksList;
