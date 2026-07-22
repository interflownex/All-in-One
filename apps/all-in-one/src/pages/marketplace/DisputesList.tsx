import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const DisputesList: React.FC = () => {
  return <SmartCRUD module="marketplace" entity="disputes" type="list" title="Disputes" />;
};

export default DisputesList;
