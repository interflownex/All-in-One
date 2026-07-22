import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const LeadsForm: React.FC = () => {
  return <SmartCRUD module="crm" entity="leads" type="form" title="Leads" />;
};

export default LeadsForm;
