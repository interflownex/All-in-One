import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const SplitsForm: React.FC = () => {
  return <SmartCRUD module="finance" entity="splits" type="form" title="Splits" />;
};

export default SplitsForm;
