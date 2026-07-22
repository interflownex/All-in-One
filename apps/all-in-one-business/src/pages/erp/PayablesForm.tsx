import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const PayablesForm: React.FC = () => {
  return <SmartCRUD module="erp" entity="payables" type="form" title="Payables" />;
};

export default PayablesForm;
