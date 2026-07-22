import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const UnitsForm: React.FC = () => {
  return <SmartCRUD module="property" entity="units" type="form" title="Units" />;
};

export default UnitsForm;
