import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const CampaignsList: React.FC = () => {
  return <SmartCRUD module="crm" entity="campaigns" type="list" title="Campaigns" />;
};

export default CampaignsList;
