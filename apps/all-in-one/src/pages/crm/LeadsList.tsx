import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const LeadsList: React.FC = () => {
  return <SmartCRUD module="crm" entity="leads" type="list" title="Leads" />;
};

export default LeadsList;
