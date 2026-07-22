import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const EvidenceList: React.FC = () => {
  return <SmartCRUD module="services" entity="evidence" type="list" title="Evidence" />;
};

export default EvidenceList;
