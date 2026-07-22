import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const LeasesList: React.FC = () => {
  return <SmartCRUD module="property" entity="leases" type="list" title="Leases" />;
};

export default LeasesList;
