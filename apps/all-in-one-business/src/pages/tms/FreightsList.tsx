import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const FreightsList: React.FC = () => {
  return <SmartCRUD module="tms" entity="freights" type="list" title="Freights" />;
};

export default FreightsList;
