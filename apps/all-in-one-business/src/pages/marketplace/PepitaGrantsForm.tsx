import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const PepitaGrantsForm: React.FC = () => {
  return <SmartCRUD module="marketplace" entity="pepitagrants" type="form" title="Pepita Grants" />;
};

export default PepitaGrantsForm;
