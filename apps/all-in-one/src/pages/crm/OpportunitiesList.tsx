import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const OpportunitiesList: React.FC = () => {
  return <SmartCRUD module="crm" entity="opportunities" type="list" title="Opportunities" />;
};

export default OpportunitiesList;
