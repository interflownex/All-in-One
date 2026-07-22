import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const BranchesForm: React.FC = () => {
  return <SmartCRUD module="business" entity="branches" type="form" title="Branches" />;
};

export default BranchesForm;
