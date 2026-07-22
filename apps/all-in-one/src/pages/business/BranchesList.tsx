import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const BranchesList: React.FC = () => {
  return <SmartCRUD module="business" entity="branches" type="list" title="Branches" />;
};

export default BranchesList;
