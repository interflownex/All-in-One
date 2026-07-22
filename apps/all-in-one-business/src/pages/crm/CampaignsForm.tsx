import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const CampaignsForm: React.FC = () => {
  return <SmartCRUD module="crm" entity="campaigns" type="form" title="Campaigns" />;
};

export default CampaignsForm;
