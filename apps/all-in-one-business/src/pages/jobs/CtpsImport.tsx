import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const CtpsImport: React.FC = () => {
  return <SmartCRUD module="jobs" entity="ctpsimport" type="form" title="Ctps Import" />;
};

export default CtpsImport;
