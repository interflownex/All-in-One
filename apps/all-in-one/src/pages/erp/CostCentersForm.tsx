import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const CostCentersForm: React.FC = () => {
  return <SmartCRUD module="erp" entity="costcenters" type="form" title="Cost Centers" />;
};

export default CostCentersForm;
