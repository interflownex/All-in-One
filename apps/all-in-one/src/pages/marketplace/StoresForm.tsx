import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const StoresForm: React.FC = () => {
  return <SmartCRUD module="marketplace" entity="stores" type="form" title="Stores" />;
};

export default StoresForm;
