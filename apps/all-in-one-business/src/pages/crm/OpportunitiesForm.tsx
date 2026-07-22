import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const OpportunitiesForm: React.FC = () => {
  return <SmartCRUD module="crm" entity="opportunities" type="form" title="Opportunities" />;
};

export default OpportunitiesForm;
