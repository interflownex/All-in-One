import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const CasesList: React.FC = () => {
  return <SmartCRUD module="legal" entity="cases" type="list" title="Cases" />;
};

export default CasesList;
